from datetime import datetime, timedelta, timezone
import secrets
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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
)
from app.core.config import settings


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


logger = logging.getLogger(__name__)


def _send_reset_email(to_email: str, token: str) -> None:
    """Send password reset email with the 6-digit token.
    Silently logs errors so the reset flow always succeeds DB-side."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Your Password Reset Code"
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = to_email

        body = (
            f"Your password reset code is: {token}\n\n"
            "This code expires in 15 minutes. If you did not request a reset, ignore this email."
        )
        msg.attach(MIMEText(body, "plain"))

        if settings.SMTP_SERVER and settings.SMTP_SERVER.lower() != "mock":
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
                logger.info(f"Reset email sent to {to_email}")
        else:
            logger.warning(f"[MOCK SMTP] Reset token for {to_email}: {token}")

    except Exception as exc:
        logger.error(f"Failed to send reset email to {to_email}: {exc}")


async def register_user(user_in: UserCreate):
    user_exists = await UserModel.find_by_email(user_in.email)
    if user_exists:
        raise UserAlreadyExistsError("User with this email already exists")

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

    if settings.SMTP_SERVER and settings.SMTP_SERVER.lower() == "mock":
        logger.warning(
            "Mock SMTP active — returning reset token in response for development."
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