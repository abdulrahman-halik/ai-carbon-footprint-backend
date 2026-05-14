from typing import Optional, Any
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    BeforeValidator,
    ConfigDict,
    field_validator,
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
    is_active: Optional[bool] = True
    onboarding_completed: Optional[bool] = False
    profile: Optional[dict] = {}


class UserCreate(UserBase):
    email: EmailStr
    password: str
    full_name: str  # Changed to required field without Optional or default

    @field_validator("full_name")
    @classmethod
    def full_name_required(cls, v):
        if not v or not v.strip():
            raise ValueError("Full name is required for registration")
        if len(v.strip()) < 3:
            raise ValueError("Full name must be at least 3 characters long")
        return v.strip()


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

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "60a2c8e0b6b2c2b3e4f5a6b7",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True,
            }
        },
    )