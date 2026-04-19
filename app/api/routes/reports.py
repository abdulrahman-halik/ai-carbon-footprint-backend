from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response

from app.api.deps import get_current_user
from app.services.report_service import generate_report_download


router = APIRouter()


@router.get("/download/{period}")
async def download_report(
    period: str,
    export_format: str = Query("csv", alias="format"),
    current_user: dict = Depends(get_current_user),
):
    try:
        content, filename, media_type = await generate_report_download(current_user, period, export_format)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return Response(content=content, media_type=media_type, headers=headers)