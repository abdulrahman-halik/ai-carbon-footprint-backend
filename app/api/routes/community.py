from fastapi import APIRouter, Depends, status, HTTPException
from app.schemas.community_schema import PostCreate, PostOut
from app.schemas.team_member_schema import TeamMemberCreate, TeamMemberUpdate, TeamMemberOut
from app.services import community_service
from app.services import team_member_service
from app.api.deps import get_current_user
from typing import List

router = APIRouter()

@router.post("/post", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_in: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    user_name = current_user.get("full_name", "Anonymous")
    return await community_service.create_post(user_id, user_name, post_in)

@router.get("/feed", response_model=List[PostOut])
async def get_feed(limit: int = 20):
    return await community_service.get_community_feed(limit=limit)

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, current_user: dict = Depends(get_current_user)):
    board = await community_service.get_leaderboard(limit=limit)
    user_id_str = str(current_user["_id"])
    for user in board:
        if user["id"] == user_id_str:
            user["isCurrentUser"] = True
    return board

# ─── Team Member CRUD ───────────────────────────────────────────────────────

@router.get("/members", response_model=List[TeamMemberOut])
async def list_members(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    return await team_member_service.get_members(user_id)

@router.post("/members", response_model=TeamMemberOut, status_code=status.HTTP_201_CREATED)
async def create_member(
    member_in: TeamMemberCreate,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    return await team_member_service.add_member(user_id, member_in)

@router.put("/members/{member_id}", response_model=TeamMemberOut)
async def update_member(
    member_id: str,
    member_in: TeamMemberUpdate,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    return await team_member_service.update_member(user_id, member_id, member_in)

@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: str,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    await team_member_service.delete_member(user_id, member_id)
