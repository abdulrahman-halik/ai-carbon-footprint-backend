from typing import List, Optional
from app.models.goal_model import GoalModel
from app.schemas.goal_schema import GoalCreate, GoalUpdate

async def set_goal(user_id: str, goal_in: GoalCreate):
    # For now, let's assume one active goal per user or per category
    # If there's an active goal for the same category, deactivate it? 
    # Or just create a new one. Requirement says "configurations".
    
    goal_dict = goal_in.model_dump()
    goal_dict["user_id"] = user_id
    
    # Check if active goal exists for this category and deactivate it
    active_goal = GoalModel.get_collection().find_one({
        "user_id": user_id, 
        "category": goal_in.category,
        "is_active": True
    })
    
    if active_goal:
        await GoalModel.update(str(active_goal["_id"]), {"is_active": False})
    
    return await GoalModel.create(goal_dict)

async def get_user_goals(user_id: str) -> List[dict]:
    return await GoalModel.find_by_user_id(user_id)

async def get_goal_progress(user_id: str):
    # In Phase 3, we don't have the emissions data yet to calculate real progress
    # So we'll return a mock progress or the goal details with 0 progress for now
    # until Phase 4 (Emissions Tracking) is implemented.
    active_goals = list(GoalModel.get_collection().find({"user_id": user_id, "is_active": True}))
    
    progress_list = []
    for goal in active_goals:
        # Placeholder for real calculation
        progress_list.append({
            "goal": goal,
            "current_value": 0.0,
            "percentage_complete": 0.0
        })
    return progress_list
