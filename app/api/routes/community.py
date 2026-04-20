from fastapi import APIRouter, Depends, status
from app.schemas.community_schema import PostCreate, PostOut
from app.services import community_service
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
