from fastapi import Depends, HTTPException, status
import logging
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.core.config import settings
from app.schemas.user_schema import TokenData
from app.models.user_model import UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            logging.error("No sub in token payload")
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError as e:
        logging.error(f"JWT decode error: {e}")
        raise credentials_exception
    
    user = await UserModel.find_by_id(user_id)
    if user is None:
        logging.error(f"User not found for id: {user_id}")
        raise credentials_exception
    return user


async def get_current_user_optional(token: str | None = Depends(oauth2_scheme_optional)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    user = await UserModel.find_by_id(user_id)
    return user
