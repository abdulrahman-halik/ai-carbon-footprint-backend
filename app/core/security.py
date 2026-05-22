import hashlib
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from app.core.config.settings import settings

def get_password_hash(password: str) -> str:
    """
    Hash password with bcrypt.
    If password > 72 bytes, hash it with SHA256 first.
    """
    if len(password.encode()) > 72:
        password = hashlib.sha256(password.encode()).hexdigest()
    
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hashed password.
    Must handle the same logic as get_password_hash.
    """
    if len(plain_password.encode()) > 72:
        plain_password = hashlib.sha256(plain_password.encode()).hexdigest()
    
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    """
    Create JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt