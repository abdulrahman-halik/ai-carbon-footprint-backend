from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from .user_schema import PyObjectId

class EmissionBase(BaseModel):
    category: str  # e.g., "Transport", "Food", "Energy", "Shopping"
    sub_category: Optional[str] = None
    value: float  # The carbon footprint value in kg CO2e
    unit: str = "kg CO2e"
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None

class EmissionCreate(EmissionBase):
    pass

class EmissionUpdate(BaseModel):
    category: Optional[str] = None
    sub_category: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None

class EmissionOut(EmissionBase):
    id: PyObjectId = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
    )
