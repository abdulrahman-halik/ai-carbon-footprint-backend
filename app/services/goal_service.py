from typing import List
from app.models.goal_model import GoalModel
from app.models.emission_model import EmissionModel
from app.schemas.goal_schema import GoalCreate


async def set_goal(user_id: str, goal_in: GoalCreate):
    goal_dict = goal_in.model_dump()
    goal_dict["user_id"] = user_id

    # Deactivate any existing active goal for the same category
    active_goal = await GoalModel.get_collection().find_one({
        "user_id": user_id,
        "category": goal_in.category,
        "is_active": True
    })

    if active_goal:
        await GoalModel.update(str(active_goal["_id"]), {"is_active": False})

    return await GoalModel.create(goal_dict)


async def get_user_goals(user_id: str) -> List[dict]:
    return await GoalModel.find_by_user_id(user_id)


async def _get_current_emissions_for_goal(user_id: str, goal: dict) -> float:
    """
    Sum emissions for the user that belong to the goal's category
    since the goal's creation date (start_date).

    For 'Overall' category, sums all emissions regardless of category.
    """
    category = goal.get("category", "")
    start_date = goal.get("created_at")  # goal tracks progress from when it was set

    # Build the DB query
    query: dict = {"user_id": user_id}
    if start_date:
        query["created_at"] = {"$gte": start_date}

    # 'Overall' means all categories; otherwise filter by category
    if category and category.lower() not in ("overall", "all"):
        query["category"] = category

    cursor = EmissionModel.get_collection().find(query, {"value": 1})
    records = await cursor.to_list(length=None)
    return sum(float(r.get("value", 0)) for r in records)


async def get_goal_progress(user_id: str):
    cursor = GoalModel.get_collection().find({"user_id": user_id, "is_active": True})
    active_goals = await cursor.to_list(length=None)

    progress_list = []
    for goal in active_goals:
        target = float(goal.get("target_value", 0) or 0)
        current = await _get_current_emissions_for_goal(user_id, goal)
        percentage = (current / target * 100) if target > 0 else 0.0
        progress_list.append({
            "goal": goal,
            "current_value": round(current, 2),
            "percentage_complete": round(min(percentage, 100.0), 1),
        })
    return progress_list
