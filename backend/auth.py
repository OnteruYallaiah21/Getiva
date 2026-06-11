import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from .config import settings
from .schemas import TokenData
from .models import UserRole


def hash_password(password: str) -> str:
    """Hash a password using bcrypt (compatible with existing passlib-generated hashes)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except (ValueError, TypeError):
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
    """Create a JWT access token.

    Returns:
        Tuple of (token, expires_in_seconds)
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    # Calculate seconds until expiration
    expires_in = int(expires_delta.total_seconds()) if expires_delta else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    return encoded_jwt, expires_in


def decode_token(token: str) -> Optional[TokenData]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        role: str = payload.get("role")
        must_change_password = payload.get("must_change_password")

        if username is None:
            return None

        token_data = TokenData(
            username=username,
            user_id=user_id,
            role=UserRole(role) if role else None,
            must_change_password=must_change_password if must_change_password is not None else None,
        )
        return token_data
    except JWTError:
        return None
