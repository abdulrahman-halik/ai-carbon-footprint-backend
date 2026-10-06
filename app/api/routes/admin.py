from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_admin
from app.services.admin_service import (
    get_all_regular_users,
    get_user_summary,
    set_user_status,
    get_emissions_analytics,
    get_water_analytics,
    get_energy_analytics,
    get_goals_analytics,
)

router = APIRouter()


class UserStatusUpdate(BaseModel):
    is_active: bool


@router.get("/users", summary="List all regular users with emission metrics")
async def list_users(admin: dict = Depends(get_current_admin)) -> Any:
    """Fetch all users whose role is 'user' for administration."""
    return await get_all_regular_users()


@router.get("/users/{user_id}/summary", summary="Get specific user's carbon emission summary")
async def user_emission_summary(
    user_id: str,
    admin: dict = Depends(get_current_admin),
) -> Any:
    """Retrieve detailed carbon emissions and resource logs for a specific user."""
    summary = await get_user_summary(user_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or invalid user identifier.",
        )
    return summary


@router.patch("/users/{user_id}/status", summary="Activate or deactivate a user")
async def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    admin: dict = Depends(get_current_admin),
) -> Any:
    """Update active status of a user (setting is_active=False blocks access)."""
    updated_user = await set_user_status(user_id, payload.is_active)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or status could not be updated.",
        )
    status_str = "activated" if payload.is_active else "deactivated"
    return {
        "success": True,
        "message": f"User has been successfully {status_str}.",
        "user": updated_user,
    }


@router.get("/analytics/emissions", summary="Carbon footprint usage comparisons across users")
async def emissions_analytics(admin: dict = Depends(get_current_admin)) -> Any:
    """Returns carbon footprint analytics, highest emitters, and categorical distributions."""
    return await get_emissions_analytics()


@router.get("/analytics/water", summary="Water usage comparisons across users")
async def water_analytics(admin: dict = Depends(get_current_admin)) -> Any:
    """Returns water usage comparisons, highest consumers, and total liters logged."""
    return await get_water_analytics()


@router.get("/analytics/energy", summary="Electricity/energy comparisons across users")
async def energy_analytics(admin: dict = Depends(get_current_admin)) -> Any:
    """Returns energy consumption comparisons, highest consumers, and source distributions."""
    return await get_energy_analytics()


@router.get("/analytics/goals", summary="Active and reducing goals analytics across users")
async def goals_analytics(admin: dict = Depends(get_current_admin)) -> Any:
    """Returns active goals, reducing goals, and user completion leaderboards."""
    return await get_goals_analytics()
