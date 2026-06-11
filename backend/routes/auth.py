from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Student, Recruiter, UserRole
from ..schemas import (
    UserRegister,
    UserLogin,
    Token,
    LoginResponse,
    UserResponse,
    UserListResponse,
    ChangePasswordRequest,
    AdminResetPasswordRequest,
)
from ..auth import hash_password, verify_password, create_access_token, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])


def get_token(authorization: str = Header(None)):
    """Extract token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format")

    return parts[1]


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    """Get current authenticated user from token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception

    return user


def require_role(*roles: UserRole):
    """Dependency to check user role."""

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return role_checker


def _token_payload(user: User) -> dict:
    return {
        "sub": user.username,
        "user_id": str(user.id),
        "role": user.role.value,
        "must_change_password": user.is_temp_password,
    }


def _resolved_user_email(user_data: UserRegister) -> str:
    """Unique, valid address for DB NOT NULL + uniqueness (omit real email → placeholder)."""
    if user_data.email:
        return str(user_data.email)
    return f"{user_data.username}@users.getiva.local"


def _provision_user(db: Session, user_data: UserRegister, *, is_temp_password: bool) -> User:
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    resolved_email = _resolved_user_email(user_data)
    existing_email = db.query(User).filter(User.email == resolved_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = User(
        username=user_data.username,
        email=resolved_email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
        is_temp_password=is_temp_password,
    )

    db.add(db_user)
    db.flush()

    if user_data.role == UserRole.STUDENT:
        student = Student(
            user_id=db_user.id,
            full_name=user_data.full_name or user_data.username,
        )
        db.add(student)
    elif user_data.role == UserRole.RECRUITER:
        recruiter = Recruiter(
            user_id=db_user.id,
            name=user_data.full_name or user_data.username,
        )
        db.add(recruiter)

    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/bootstrap", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_first_admin(user_data: UserRegister, db: Session = Depends(get_db)):
    """Create the first (bootstrap) administrator when no users exist. Disabled once any user exists."""
    if db.query(User).count() > 0:
        raise HTTPException(
            status_code=403,
            detail="Bootstrap is disabled. Sign in as an administrator to create users.",
        )
    if user_data.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=400,
            detail="The first user must be an administrator.",
        )
    return _provision_user(db, user_data, is_temp_password=False)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def admin_create_user(
    user_data: UserRegister,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """Create a student, recruiter, or admin account (admin only). New accounts use a temporary password until first change."""
    is_temp = True
    return _provision_user(db, user_data, is_temp_password=is_temp)


@router.get("/users", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """List users (admin only)."""
    q = db.query(User)
    total = q.count()
    rows = (
        q.order_by(User.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return UserListResponse(
        items=rows,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.patch("/users/{user_id}/toggle-status", response_model=UserResponse)
def toggle_user_status(
    user_id: UUID,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """Enable or disable a user account (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = 0 if user.is_active else 1
    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reset-password", response_model=UserResponse)
def admin_reset_user_password(
    user_id: UUID,
    body: AdminResetPasswordRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """Set a new password for any user (students, recruiters, admins). Existing passwords cannot be read—only replaced.

    The user must sign in with the new password; `is_temp_password` is set so they should change it after login if you use a temporary value.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(body.new_password)
    user.is_temp_password = True
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's profile."""
    return current_user


@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    access_token, expires_in = create_access_token(data=_token_payload(user))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        must_change_password=user.is_temp_password,
    )


@router.post("/change-password", response_model=LoginResponse)
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Change password (required after login with a temporary password)."""
    if not verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    if body.current_password == body.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from the current password")

    current_user.password_hash = hash_password(body.new_password)
    current_user.is_temp_password = False
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    access_token, expires_in = create_access_token(data=_token_payload(current_user))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        must_change_password=False,
    )


@router.post("/logout")
def logout():
    """Logout endpoint (token invalidation handled client-side)."""
    return {"message": "Successfully logged out"}


@router.post("/refresh-token", response_model=LoginResponse)
def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token."""
    access_token, expires_in = create_access_token(data=_token_payload(current_user))

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        must_change_password=current_user.is_temp_password,
    )

