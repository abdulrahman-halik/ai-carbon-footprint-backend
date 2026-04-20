from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from app.services import report_service
from app.api.deps import get_current_user
import io

router = APIRouter()

@router.get("/download/{period}")
async def download_report(
    period: str,
    current_user: dict = Depends(get_current_user)
):
    if period not in ["monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Period must be 'monthly' or 'yearly'")
    
    user_id = str(current_user["_id"])
    csv_data = await report_service.generate_user_report_csv(user_id, period)
    
    buffer = io.BytesIO(csv_data.encode("utf-8"))
    
    filename = f"sustainability_report_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# For filename timestamp
from datetime import datetime
