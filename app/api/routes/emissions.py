from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.api.deps import get_current_user
from app.schemas.emission_schema import EmissionCreate, EmissionOut, EmissionUpdate
from app.services.emission_service import (
    log_emission, get_user_emissions, get_emission_by_id, update_emission, delete_emission, get_emission_stats
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


@router.get("/stats")
async def emission_stats(current_user: dict = Depends(get_current_user)):
    return await get_emission_stats(str(current_user["_id"]))


@router.get("/{record_id}", response_model=EmissionOut)
async def get_emission(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format. Must be a 24-character hexadecimal string."
        )
    emission = await get_emission_by_id(record_id, str(current_user["_id"]))
    if not emission:
        raise HTTPException(status_code=404, detail="Emission record not found or access denied")
    return emission


@router.put("/{record_id}", response_model=EmissionOut)
async def update_emission_record(
    record_id: str,
    update_data: EmissionUpdate,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format. Must be a 24-character hexadecimal string."
        )
    # Fix #8: pass user_id to enforce ownership — only the owner can update
    updated = await update_emission(record_id, update_data, user_id=str(current_user["_id"]))
    if not updated:
        raise HTTPException(status_code=404, detail="Emission record not found or access denied")
    return updated


@router.delete("/{record_id}")
async def delete_emission_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    if not ObjectId.is_valid(record_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid record ID format. Must be a 24-character hexadecimal string."
        )
    # Fix #8: pass user_id to enforce ownership — only the owner can delete
    success = await delete_emission(record_id, user_id=str(current_user["_id"]))
    if not success:
        raise HTTPException(status_code=404, detail="Emission record not found or access denied")
    return {"message": "Emission record deleted"}
