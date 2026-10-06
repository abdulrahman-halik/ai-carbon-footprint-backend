from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import get_current_user
from app.schemas.user_schema import (
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    Token,
    UserCreate,
    UserOut,
    UserLogin,
    VerifyOTPRequest,
    VerifyOTPResponse,
    LoginResponse,
)
from app.services.auth_service import (
    authenticate_user,
    change_user_password,
    confirm_password_reset,
    create_user_token,
    register_user,
    request_password_reset,
    verify_user_otp,
    InvalidPasswordError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidTokenError,
    PasswordMismatchError,
    InvalidOTPError,
    UserNotActiveError,
)

router = APIRouter()


# AUTHENTICATION & REGISTRATION

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(user_in: UserCreate) -> Any:
    """Creates a new user account with the provided details."""
    try:
        return await register_user(user_in)
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/verify-otp",
    response_model=VerifyOTPResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify OTP and activate account"
)
async def verify_otp(verify_data: VerifyOTPRequest) -> Any:
    """Validates the OTP code for an email and activates the user account."""
    try:
        return await verify_user_otp(verify_data)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except InvalidOTPError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login", 
    response_model=LoginResponse,
    summary="User login for access token"
)
async def login(request: Request) -> Any:
    """
    Logs in a user. Accepts either 'email' or 'username' alongside 'password'.
    Expects a strict JSON body payload.
    """
    try:
        body: Dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload provided."
        )

    # Normalize 'username' to 'email' field if provided instead
    if "username" in body and "email" not in body:
        body["email"] = body["username"]

    if not body.get("email") or not body.get("password"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credentials missing. Both (email or username) and password are required."
        )

    # Use the Pydantic schema to parse and validate the dict payload structured above
    try:
        user_login = UserLogin(**body)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    
    try:
        user = await authenticate_user(user_login)
    except UserNotActiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = await create_user_token(str(user["_id"]))
    return LoginResponse(
        message="Activated successfully",
        access_token=token.access_token,
        token_type=token.token_type,
        user=UserOut(**user),
    )


# PASSWORD MANAGEMENT

@router.post("/forgot-password", summary="Request password reset token")
async def forgot_password(forgot_data: PasswordResetRequest) -> Any:
    """Sends a password reset link/token to the user's registered email."""
    try:
        return await request_password_reset(forgot_data)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/reset-password", summary="Reset password using token")
async def reset_password(reset_data: PasswordResetConfirm) -> Any:
    """Resets the user's password using a valid token."""
    try:
        return await confirm_password_reset(reset_data)
    except (InvalidTokenError, PasswordMismatchError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/change-password", summary="Change current user password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
) -> Any:
    """Changes the password for the currently authenticated user."""
    # Front-end constraint rule checked at the API boundary
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from the current password.",
        )

    try:
        await change_user_password(str(current_user["_id"]), password_data)
        return {"success": True, "message": "Password changed successfully."}
        
    except InvalidPasswordError as e:
        # Handles clean translation of service exception to user-facing HTTP 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )