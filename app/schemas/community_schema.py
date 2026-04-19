from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .user_schema import PyObjectId


class CommunityPostCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=500)
    post_type: str = Field(default="milestone", min_length=3, max_length=40)
    milestone_label: Optional[str] = Field(default=None, max_length=80)


class CommunityPostOut(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    user_id: str
    author_name: str
    content: str
    post_type: str
    milestone_label: Optional[str] = None
    logging_streak_days: int = 0
    contribution_count: int = 0
    was_sanitized: bool = False
    created_at: datetime

    class Config:
        populate_by_name = True