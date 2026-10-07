from datetime import datetime, timedelta, timezone
import secrets
import logging
import resend
from fastapi import HTTPException, status

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.models.user_model import UserModel
from app.schemas.user_schema import (
    UserCreate,
    UserLogin,
    Token,
    PasswordChange,
    PasswordResetRequest,
    PasswordResetConfirm,
    VerifyOTPRequest,
)
from app.core.config import settings

if settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY

class AuthServiceError(Exception):
    """Base exception for auth service."""
    pass


class UserAlreadyExistsError(AuthServiceError):
    pass


class UserNotFoundError(AuthServiceError):
    pass


class InvalidTokenError(AuthServiceError):
    pass


class CredentialError(AuthServiceError):
    pass


class InvalidPasswordError(AuthServiceError):
    pass


class PasswordMismatchError(AuthServiceError):
    pass


class InvalidOTPError(AuthServiceError):
    pass


class UserNotActiveError(AuthServiceError):
    pass


logger = logging.getLogger(__name__)


def _send_reset_email(to_email: str, token: str) -> None:
    """Send password reset email with the 6-digit token.
    Silently logs errors so the reset flow always succeeds DB-side."""
    try:
        if settings.RESEND_API_KEY:
            logger.info(f"Sending reset email to {to_email} via Resend")
            
            html_body = f"""
            <p>Your password reset code is: <strong>{token}</strong></p>
            <p>This code expires in 15 minutes. If you did not request a reset, ignore this email.</p>
            """
            
            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": "Your Password Reset Code",
                "html": html_body,
            }
            
            email_response = resend.Emails.send(params)
            logger.info(f"Reset email successfully sent to {to_email}. Resend ID: {email_response.get('id')}")
        else:
            logger.warning(f"[MOCK EMAIL / NO RESEND KEY] Reset token for {to_email}: {token}")

    except Exception as exc:
        logger.error(f"Failed to send reset email to {to_email}: {exc}", exc_info=True)


def _send_otp_email(to_email: str, otp_code: str) -> None:
    """Send account activation email with the 6-digit verification code using Resend.
    Silently logs errors so registration succeeds DB-side."""
    try:
        if settings.RESEND_API_KEY:
            logger.info(f"Sending activation email to {to_email} via Resend")
            
            html_body = f"""
            <p>Your account activation code is: <strong>{otp_code}</strong></p>
            <p>This code expires in 15 minutes. Please use this code to activate your account.</p>
            """
            
            params = {
                "from": settings.RESEND_FROM_EMAIL,
                "to": [to_email],
                "subject": "Your Account Activation Code",
                "html": html_body,
            }
            
            email_response = resend.Emails.send(params)
            logger.info(f"Activation email successfully sent to {to_email}. Resend ID: {email_response.get('id')}")
        else:
            logger.warning(f"[MOCK EMAIL / NO RESEND KEY] Verification OTP for {to_email}: {otp_code}")

    except Exception as exc:
        logger.error(f"Failed to send activation email to {to_email}: {exc}", exc_info=True)


async def register_user(user_in: UserCreate):
    user_exists = await UserModel.find_by_email(user_in.email)
    if user_exists:
        raise UserAlreadyExistsError("User with this email already exists")

    user_dict = user_in.model_dump()
    user_dict["password"] = get_password_hash(user_dict["password"])
    # 1. When customer creates account, by default is_active is active so they can login immediately
    user_dict["is_active"] = True
    user_dict["role"] = "user"
    user_dict["created_at"] = datetime.now(timezone.utc)

    # 2. Generate 6-digit random OTP code
    otp_code = "".join(secrets.choice("0123456789") for _ in range(6))
    otp_expires_at = datetime.now(timezone.utc) + timedelta(minutes=1440)
    user_dict["otp_code"] = otp_code
    user_dict["otp_expires_at"] = otp_expires_at

    user = await UserModel.create(user_dict)
    _send_otp_email(user_in.email, otp_code)
    return user


async def verify_user_otp(verify_data: VerifyOTPRequest):
    user = await UserModel.find_by_email(verify_data.email)
    if not user:
        raise UserNotFoundError("User with this email does not exist.")

    if user.get("is_active") is True:
        return {"message": "Account is already activated.", "is_active": True}

    submitted_otp = verify_data.otp_code or verify_data.otp
    stored_otp = user.get("otp_code")
    otp_expiry = user.get("otp_expires_at")

    if not stored_otp or str(stored_otp) != str(submitted_otp):
        raise InvalidOTPError("Invalid verification code.")

    if otp_expiry:
        if otp_expiry.tzinfo is None:
            otp_expiry = otp_expiry.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > otp_expiry:
            raise InvalidOTPError("Verification code has expired. Please request a new one.")

    # 3. If both match, set is_active to True and clear OTP
    await UserModel.update(
        str(user["_id"]),
        {
            "is_active": True,
            "otp_code": None,
            "otp_expires_at": None,
        },
    )

    return {"message": "Account successfully activated.", "is_active": True}


async def authenticate_user(user_login: UserLogin):
    user = await UserModel.find_by_email(user_login.email)
    if not user:
        return None
    if not verify_password(user_login.password, user["password"]):
        return None
    # 4. Check if is_active is False
    # Enforce active check as per instructions instead of explicitly bypassing
    if not user.get("is_active", False):
        raise UserNotActiveError("Your account has been deactivated. Please contact an administrator.")
    return user


async def create_user_token(user_id: str):
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        subject=user_id,
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


async def change_user_password(user_id: str, password_data: PasswordChange):
    user = await UserModel.find_by_id(user_id)

    if not user or not verify_password(
        password_data.current_password,
        user["password"],
    ):
        raise InvalidPasswordError("Current password is incorrect.")

    hashed_password = get_password_hash(password_data.new_password)

    return await UserModel.update(user_id, {"password": hashed_password})


async def request_password_reset(reset_data: PasswordResetRequest):
    user = await UserModel.find_by_email(reset_data.email)

    if not user:
        raise UserNotFoundError("Email does not exist.")

    reset_token = "".join(secrets.choice("0123456789") for _ in range(6))
    expires = datetime.now(timezone.utc) + timedelta(minutes=15)

    await UserModel.update(
        str(user["_id"]),
        {
            "reset_token": reset_token,
            "reset_token_expires": expires,
        },
    )

    _send_reset_email(reset_data.email, reset_token)

    if not settings.RESEND_API_KEY:
        logger.warning(
            "Mock email active — returning reset token in response for development."
        )
        return {
            "message": "Reset instructions have been sent to the email address provided.",
            "reset_token": reset_token,
        }

    return {
        "message": "Reset instructions have been sent to the email address provided."
    }


async def confirm_password_reset(reset_data: PasswordResetConfirm):
    user = await UserModel.find_by_email(reset_data.email)

    if not user:
        raise InvalidTokenError("Invalid or expired reset token.")

    stored_token = user.get("reset_token")
    token_expiry = user.get("reset_token_expires")

    if not stored_token or not token_expiry:
        raise InvalidTokenError("Invalid or expired reset token.")

    if reset_data.token != stored_token:
        raise InvalidTokenError("Invalid or expired reset token.")

    if token_expiry.tzinfo is None:
        token_expiry = token_expiry.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > token_expiry:
        raise InvalidTokenError("Invalid or expired reset token.")

    if reset_data.password != reset_data.confirm_password:
        raise PasswordMismatchError("Passwords do not match")

    hashed_password = get_password_hash(reset_data.password)

    await UserModel.update(
        str(user["_id"]),
        {
            "password": hashed_password,
            "reset_token": None,
            "reset_token_expires": None,
        },
    )

    return {"message": "Password has been successfully reset."}