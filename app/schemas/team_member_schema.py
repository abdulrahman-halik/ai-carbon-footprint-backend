from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TeamMemberCreate(BaseModel):
    name: str
    email: str
    role: str = "Member"
    status: str = "Active"
    avatar: Optional[str] = None
    task: Optional[str] = "No task yet"


class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    avatar: Optional[str] = None
    task: Optional[str] = None


class TeamMemberOut(BaseModel):
    id: str
    user_id: str
    name: str
    email: str
    role: str
    status: str
    avatar: Optional[str] = None
    task: Optional[str] = "No task yet"
    statusColor: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @classmethod
    def from_mongo(cls, data: dict):
        if not data:
            return None
        data = dict(data)
        doc_id = str(data.pop("_id"))
        # Build statusColor based on status
        status_colors = {
            "Active": "bg-emerald-100 text-emerald-700",
            "Inactive": "bg-gray-100 text-gray-500",
            "In Progress": "bg-amber-100 text-amber-700",
        }
        status = data.get("status", "Active")
        data.setdefault("statusColor", status_colors.get(status, "bg-gray-100 text-gray-500"))
        return cls(id=doc_id, **data)
