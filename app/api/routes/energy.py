from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.schemas.energy_schema import EnergyCreate, EnergyOut, EnergyUpdate
from app.services.energy_service import (
    log_energy, get_user_energy_logs, update_energy_log, delete_energy_log
)

router = APIRouter()

@router.post("/", response_model=EnergyOut)
async def create_energy_log(
    energy_in: EnergyCreate,
    current_user: dict = Depends(get_current_user)
):
    return await log_energy(str(current_user["_id"]), energy_in)

@router.get("/", response_model=List[EnergyOut])
async def list_energy_logs(current_user: dict = Depends(get_current_user)):
    return await get_user_energy_logs(str(current_user["_id"]))

@router.put("/{record_id}", response_model=EnergyOut)
async def update_energy_record(
    record_id: str,
    update_data: EnergyUpdate,
    current_user: dict = Depends(get_current_user)
):
    updated = await update_energy_log(record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Energy log not found")
    return updated

@router.delete("/{record_id}")
async def delete_energy_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    success = await delete_energy_log(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Energy log not found")
    return {"message": "Energy log deleted"}
