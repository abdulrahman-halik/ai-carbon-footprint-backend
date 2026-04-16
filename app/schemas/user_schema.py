from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, BeforeValidator
from typing_extensions import Annotated

# Handle MongoDB ObjectId by converting to string
PyObjectId = Annotated[str, BeforeValidator(str)]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    onboarding_completed: Optional[bool] = False
    profile: Optional[dict] = {}

class OnboardingStart(BaseModel):
    # This might be empty or contain initial setup data
    pass

class OnboardingComplete(BaseModel):
    profile: dict

class UserCreate(UserBase):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserOut(UserBase):
    id: PyObjectId = Field(..., alias="_id")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "60a2c8e0b6b2c2b3e4f5a6b7",
                "email": "user@example.com",
                "full_name": "John Doe",
                "is_active": True
            }
        }
