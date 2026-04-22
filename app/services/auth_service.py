from datetime import datetime, timedelta, timezone
import secrets
import anyio
from fastapi import HTTPException, status
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user_model import UserModel
from app.schemas.user_schema import (
    UserCreate, UserLogin, Token, PasswordChange, TwoFAToggle, 
    PasswordResetRequest, PasswordResetConfirm
)
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

async def change_user_password(user_id: str, password_data: PasswordChange):
    user = await UserModel.find_by_id(user_id)
    if not user or not verify_password(password_data.current_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )
    
    hashed_password = get_password_hash(password_data.new_password)
    return await UserModel.update(user_id, {"password": hashed_password})

async def toggle_user_2fa(user_id: str, two_fa_data: TwoFAToggle):
    # This assumes a 'two_fa_enabled' field in the user model/profile
    return await UserModel.update(user_id, {"two_fa_enabled": two_fa_data.enabled})

async def request_password_reset(reset_data: PasswordResetRequest):
    user = await UserModel.find_by_email(reset_data.email)
    
    # Generic message regardless of whether user exists
    message = "If the email exists, reset instructions have been sent."
    
    if user:
        # Generate a secure 6-digit token
        reset_token = "".join(secrets.choice("0123456789") for _ in range(6))
        # Valid for 15 minutes
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        
        await UserModel.update(str(user["_id"]), {
            "reset_token": reset_token,
            "reset_token_expires": expires
        })
    
    return {"message": message}

async def confirm_password_reset(reset_data: PasswordResetConfirm):
    user = await UserModel.find_by_email(reset_data.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email",
        )
    
    if reset_data.password != reset_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )
    
    hashed_password = get_password_hash(reset_data.password)
    await UserModel.update(str(user["_id"]), {
        "password": hashed_password,
        "reset_token": None,
        "reset_token_expires": None
    })
    
    return {"message": "Password has been successfully reset."}
