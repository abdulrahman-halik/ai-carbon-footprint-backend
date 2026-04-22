from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from app.schemas.user_schema import (
    UserCreate, UserOut, Token, UserLogin, PasswordChange, TwoFAToggle, 
    PasswordResetRequest, PasswordResetConfirm
)
from app.services.auth_service import (
    register_user, authenticate_user, create_user_token, change_user_password, toggle_user_2fa, 
    request_password_reset, confirm_password_reset
)
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    return await register_user(user_in)

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    username: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
):
    # Support both username and email 
    login_email = email or username
    
    if login_email and password:
        user_login = UserLogin(email=login_email, password=password)
    else:
        try:
            body = await request.json()
            if "username" in body and "email" not in body:
                body["email"] = body["username"]
            user_login = UserLogin(**body)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing or invalid credentials. Provide 'email' and 'password' as Form or JSON data."
            )

    user = await authenticate_user(user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await create_user_token(str(user["_id"]))

@router.post("/forgot-password")
async def forgot_password(forgot_data: PasswordResetRequest):
    return await request_password_reset(forgot_data)

@router.post("/reset-password")
async def reset_password(reset_data: PasswordResetConfirm):
    return await confirm_password_reset(reset_data)

@router.put("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    await change_user_password(str(current_user["_id"]), password_data)
    return {"message": "Password changed successfully"}

@router.put("/2fa")
async def toggle_2fa(
    two_fa_data: TwoFAToggle,
    current_user: dict = Depends(get_current_user)
):
    await toggle_user_2fa(str(current_user["_id"]), two_fa_data)
    return {"message": f"2FA {'enabled' if two_fa_data.enabled else 'disabled'} successfully"}
