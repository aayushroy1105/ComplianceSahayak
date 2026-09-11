from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime, timezone
from app.db.session import get_db
from app.models.report import Report
from app.models.inspection import Inspection
from app.schemas.report import ReportResponse

router = APIRouter()

import hashlib

@router.get("/report/{raw_token}", response_model=ReportResponse)
async def get_shared_report(raw_token: str, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await db.execute(select(Report).where(Report.share_token_hash == token_hash))
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="Shared report not found")

    if report.share_expires_at and report.share_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Shared link has expired")

    # In a real shared report, we'd limit data or sign URLs specifically for public viewing.
    # For now, we return the standard ReportResponse which contains report_path.
    return report

from fastapi.responses import FileResponse

@router.get("/report/{raw_token}/download")
async def download_shared_report(raw_token: str, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    result = await db.execute(select(Report).where(Report.share_token_hash == token_hash))
    report = result.scalars().first()

    if not report:
        raise HTTPException(status_code=404, detail="Shared report not found")

    if report.share_expires_at and report.share_expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Shared link has expired")

    import os
    from app.core.config import settings

    file_path = report.report_path
    if not os.path.isabs(file_path):
        file_path = os.path.join(settings.ABSOLUTE_UPLOAD_DIR, os.path.basename(file_path))

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found on server")

    filename = f"Shared_Report_{report.inspection_id}.md"
    return FileResponse(path=file_path, filename=filename, media_type='text/markdown')
