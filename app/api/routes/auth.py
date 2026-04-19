from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user_schema import UserCreate, UserOut, Token, UserLogin
from app.services.auth_service import register_user, authenticate_user, create_user_token
from app.core.security import create_refresh_token, decode_refresh_token
from app.models.user_model import UserModel

router = APIRouter()

_REFRESH_COOKIE = "refresh_token"
_COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate):
    return await register_user(user_in)


@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(UserLogin(email=form_data.username, password=form_data.password))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = str(user["_id"])
    token = await create_user_token(user_id)

    # Set refresh token as HTTP-only cookie so it is never readable by JS
    refresh_token = create_refresh_token(user_id)
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=False,   # Set True in production (HTTPS)
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/auth",
    )
    return token


@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: Request, response: Response):
    """Issue a new access token using the HTTP-only refresh token cookie."""
    raw_token = request.cookies.get(_REFRESH_COOKIE)
    if not raw_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No refresh token")

    user_id = decode_refresh_token(raw_token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")

    user = await UserModel.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_token = await create_user_token(user_id)

    # Rotate the refresh token on each use (prevents token-reuse attacks)
    new_refresh = create_refresh_token(user_id)
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=new_refresh,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/auth",
    )
    return new_token


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response):
    """Clear the refresh token cookie."""
    response.delete_cookie(key=_REFRESH_COOKIE, path="/api/auth")


@router.post("/forgot-password")
async def forgot_password():
    return {"message": "Password reset functionality is not implemented yet. Please contact support."}
