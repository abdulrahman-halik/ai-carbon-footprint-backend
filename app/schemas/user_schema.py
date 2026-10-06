from typing import Optional, Any
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    BeforeValidator,
    ConfigDict,
    model_validator,
)
from typing_extensions import Annotated


# Convert MongoDB ObjectId -> string
PyObjectId = Annotated[str, BeforeValidator(str)]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class UserBase(BaseModel):
    is_active: Optional[bool] = False
    onboarding_completed: Optional[bool] = False
    role: Optional[str] = "user"
    profile: Optional[dict] = {}


class UserCreate(UserBase):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: Optional[str] = None
    password: str
    confirm_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class TwoFAToggle(BaseModel):
    enabled: bool


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    profile: Optional[dict] = None


class OnboardingComplete(BaseModel):
    profile: dict


class OnboardingStart(BaseModel):
    pass


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserOut(UserBase):
    id: PyObjectId = Field(..., alias="_id")
    email: EmailStr
    full_name: str
    role: str = "user"

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "60a2c8e0b6b2c2b3e4f5a6b7",
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "user",
                "is_active": False,
            }
        },
    )


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: Optional[str] = None
    otp: Optional[str] = None

    @model_validator(mode="after")
    def validate_otp(self):
        code = self.otp_code or self.otp
        if not code:
            raise ValueError("OTP code is required.")
        self.otp_code = str(code).strip()
        return self


class VerifyOTPResponse(BaseModel):
    message: str = "Account successfully activated."
    is_active: bool = True


class LoginResponse(BaseModel):
    message: str = "Activated successfully"
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None