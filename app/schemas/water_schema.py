from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .user_schema import PyObjectId

class WaterBase(BaseModel):
    value: float
    unit: str = "L"  # Liters, or "m3" for Cubic Meters
    date: datetime = Field(default_factory=datetime.utcnow)

class WaterCreate(WaterBase):
    pass

class WaterUpdate(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[datetime] = None

class WaterOut(WaterBase):
    id: PyObjectId = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
