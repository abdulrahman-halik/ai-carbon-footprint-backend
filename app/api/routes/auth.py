from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from app.schemas.user_schema import (
    UserCreate, UserOut, Token, UserLogin, PasswordChange, TwoFAToggle
)
from app.services.auth_service import (
    register_user, authenticate_user, create_user_token, change_user_password, toggle_user_2fa
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
    password: Optional[str] = Form(None),
):
    if username and password:
        user_login = UserLogin(email=username, password=password)
    else:
        body = await request.json()
        if "username" in body and "email" not in body:
            body["email"] = body["username"]
        user_login = UserLogin(**body)

    user = await authenticate_user(user_login)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await create_user_token(str(user["_id"]))

@router.post("/forgot-password")
async def forgot_password():
    return {"message": "Password reset functionality is not implemented yet. Please contact support."}

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
