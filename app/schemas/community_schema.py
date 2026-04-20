from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class PostBase(BaseModel):
    content: str
    post_type: str = "general" # streak, milestone, general

class PostCreate(PostBase):
    pass

class PostOut(PostBase):
    id: str
    user_id: str
    user_name: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return None
        id = str(data.pop("_id"))
        return cls(id=id, **data)
