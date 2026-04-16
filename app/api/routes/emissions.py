from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.schemas.emission_schema import EmissionCreate, EmissionOut, EmissionUpdate
from app.services.emission_service import (
    log_emission, get_user_emissions, update_emission, delete_emission, get_emission_stats
)

router = APIRouter()

@router.post("/", response_model=EmissionOut)
async def create_emission(
    emission_in: EmissionCreate,
    current_user: dict = Depends(get_current_user)
):
    return await log_emission(str(current_user["_id"]), emission_in)

@router.get("/", response_model=List[EmissionOut])
async def list_emissions(current_user: dict = Depends(get_current_user)):
    return await get_user_emissions(str(current_user["_id"]))

@router.put("/{record_id}", response_model=EmissionOut)
async def update_emission_record(
    record_id: str,
    update_data: EmissionUpdate,
    current_user: dict = Depends(get_current_user)
):
    updated = await update_emission(record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Emission record not found")
    return updated

@router.delete("/{record_id}")
async def delete_emission_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    success = await delete_emission(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Emission record not found")
    return {"message": "Emission record deleted"}

@router.get("/stats")
async def emission_stats(current_user: dict = Depends(get_current_user)):
    return await get_emission_stats(str(current_user["_id"]))
