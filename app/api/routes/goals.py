from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.schemas.goal_schema import GoalCreate, GoalOut, GoalProgress
from app.services.goal_service import set_goal, get_goal_progress

router = APIRouter()

@router.post("/set", response_model=GoalOut)
async def goal_set(
    goal_in: GoalCreate,
    current_user: dict = Depends(get_current_user)
):
    return await set_goal(str(current_user["_id"]), goal_in)

@router.get("/progress", response_model=List[GoalProgress])
async def goal_progress(current_user: dict = Depends(get_current_user)):
    return await get_goal_progress(str(current_user["_id"]))
