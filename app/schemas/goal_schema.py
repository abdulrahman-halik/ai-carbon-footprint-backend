from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from .user_schema import PyObjectId

class GoalBase(BaseModel):
    target_value: float
    target_date: Optional[datetime] = None
    is_active: bool = True
    category: str  # e.g., "Food", "Shopping", "Overall"

class GoalCreate(GoalBase):
    pass

class GoalUpdate(BaseModel):
    target_value: Optional[float] = None
    target_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class GoalOut(GoalBase):
    id: PyObjectId = Field(..., alias="_id")
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

class GoalProgress(BaseModel):
    goal: GoalOut
    current_value: float
    percentage_complete: float
