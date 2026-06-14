from app.models.team_member_model import TeamMemberModel
from app.schemas.team_member_schema import TeamMemberCreate, TeamMemberUpdate, TeamMemberOut
from fastapi import HTTPException, status
from typing import List


async def add_member(user_id: str, data: TeamMemberCreate) -> TeamMemberOut:
    member_dict = data.model_dump()
    member_dict["user_id"] = user_id
    # Set avatar fallback
    if not member_dict.get("avatar"):
        member_dict["avatar"] = f"https://i.pravatar.cc/150?u={member_dict['email']}"
    doc = await TeamMemberModel.create(member_dict)
    return TeamMemberOut.from_mongo(doc)


async def get_members(user_id: str) -> List[TeamMemberOut]:
    docs = await TeamMemberModel.find_by_user_id(user_id)
    return [TeamMemberOut.from_mongo(d) for d in docs]


async def update_member(user_id: str, member_id: str, data: TeamMemberUpdate) -> TeamMemberOut:
    existing = await TeamMemberModel.find_by_id(member_id, user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    updated = await TeamMemberModel.update(member_id, user_id, update_data)
    return TeamMemberOut.from_mongo(updated)


async def delete_member(user_id: str, member_id: str) -> bool:
    existing = await TeamMemberModel.find_by_id(member_id, user_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    return await TeamMemberModel.delete(member_id, user_id)
