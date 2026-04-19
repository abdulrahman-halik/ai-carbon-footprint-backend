from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user
from app.schemas.community_schema import CommunityPostCreate, CommunityPostOut
from app.services.community_service import create_community_post, get_community_feed


router = APIRouter()


@router.get("/feed", response_model=List[CommunityPostOut])
async def community_feed(limit: int = Query(20, ge=1, le=50)):
    return await get_community_feed(limit=limit)


@router.post("/post", response_model=CommunityPostOut, status_code=status.HTTP_201_CREATED)
async def community_post(
    payload: CommunityPostCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        return await create_community_post(current_user, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))