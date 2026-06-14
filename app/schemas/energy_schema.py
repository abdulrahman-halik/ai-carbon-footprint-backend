from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, timezone
from .user_schema import PyObjectId

class EnergyBase(BaseModel):
    energy_type: str  # e.g., "Electricity", "Natural Gas", "Heating Oil"
    value: float
    unit: str  # e.g., "kWh", "m3", "L"
    notes: Optional[str] = None
    date: datetime = Field(default_factory=datetime.utcnow)

class EnergyCreate(EnergyBase):
    pass

class EnergyUpdate(BaseModel):
    energy_type: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    date: Optional[datetime] = None

class EnergyOut(EnergyBase):
    id: PyObjectId = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
    )
