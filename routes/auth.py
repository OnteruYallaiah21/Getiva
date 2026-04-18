from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from models import User, Student, Recruiter, UserRole
from schemas import UserRegister, UserLogin, Token, UserResponse
from auth import hash_password, verify_password, create_access_token
from config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
    )

    db.add(db_user)
    db.flush()

    # Create role-specific profiles
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


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is disabled")

    # Create access token
    access_token, expires_in = create_access_token(
        data={
            "sub": user.username,
            "user_id": str(user.id),
            "role": user.role.value,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


@router.post("/logout")
def logout():
    """Logout endpoint (token invalidation handled client-side)."""
    return {"message": "Successfully logged out"}


@router.post("/refresh-token", response_model=Token)
def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token."""
    access_token, expires_in = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": str(current_user.id),
            "role": current_user.role.value,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    """Get current authenticated user from token."""
    from auth import decode_token

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


def get_token(authorization: str = None):
    """Extract token from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format")

    return parts[1]


def require_role(*roles: UserRole):
    """Dependency to check user role."""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return role_checker
