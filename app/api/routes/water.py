from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from app.schemas.water_schema import WaterCreate, WaterOut, WaterUpdate
from app.services.water_service import (
    log_water_usage, get_user_water_logs, update_water_log, delete_water_log
)

router = APIRouter()

@router.post("/", response_model=WaterOut)
async def create_water_log(
    water_in: WaterCreate,
    current_user: dict = Depends(get_current_user)
):
    return await log_water_usage(str(current_user["_id"]), water_in)

@router.get("/", response_model=List[WaterOut])
async def list_water_logs(current_user: dict = Depends(get_current_user)):
    return await get_user_water_logs(str(current_user["_id"]))

@router.put("/{record_id}", response_model=WaterOut)
async def update_water_record(
    record_id: str,
    update_data: WaterUpdate,
    current_user: dict = Depends(get_current_user)
):
    updated = await update_water_log(record_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Water log not found")
    return updated

@router.delete("/{record_id}")
async def delete_water_record(
    record_id: str,
    current_user: dict = Depends(get_current_user)
):
    success = await delete_water_log(record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Water log not found")
    return {"message": "Water log deleted"}
