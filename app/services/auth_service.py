from datetime import timedelta
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreate, UserLogin, Token
from app.core.config import settings

async def register_user(user_in: UserCreate):
    user_exists = await UserModel.find_by_email(user_in.email)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    user_dict = user_in.model_dump()
    user_dict["password"] = get_password_hash(user_dict["password"])
    
    user = await UserModel.create(user_dict)
    return user

async def authenticate_user(user_login: UserLogin):
    user = await UserModel.find_by_email(user_login.email)
    if not user:
        return False
    if not verify_password(user_login.password, user["password"]):
        return False
    return user

async def create_user_token(user_id: str):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user_id, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
