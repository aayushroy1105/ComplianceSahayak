from fastapi import APIRouter, Depends, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from app.api.dependencies import get_db, require_user, require_officer
from app.models.user import User
from app.models.notice import EnforcementNotice
from app.schemas.inspection import (
    InspectionCreateRequest, 
    InspectionCreateResponse, 
    InspectionListResponse, 
    InspectionDetailResponse,
    InspectionListItem,
    Pagination,
    ViolationResponse,
    EvidenceResponse,
    LocationMarkersResponse
)
from app.schemas.notice import NoticeCreate, NoticeResponse
from app.schemas.report import ReportResponse, ShareResponse
from app.schemas.inspection_image import InspectionImageResponse
from app.services.inspection_service import (
    create_inspection as service_create_inspection,
    get_inspection as service_get_inspection,
    list_inspections as service_list_inspections,
    upload_inspection_image
)
from app.services.report_service import generate_report_for_inspection, get_latest_report_for_inspection
from app.services.analysis_service import process_inspection_analysis
from app.clients.ai_client import AIServiceClient
from app.schemas.ai_result import AIAnalyzeResponse

ai_client_instance = AIServiceClient()

router = APIRouter()

@router.post("", response_model=InspectionCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection_endpoint(
    data: InspectionCreateRequest,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new inspection.
    """
    inspection = await service_create_inspection(db, current_user, data)
    await db.commit()
    await db.refresh(inspection)
    return inspection

@router.get("", response_model=InspectionListResponse)
async def list_inspections_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    compliance_status: Optional[str] = None,
    processing_status: Optional[str] = None,
    q: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    scope: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List inspections with pagination and filtering.
    """
    from datetime import datetime
    
    start_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
        except ValueError:
            pass
            
    end_dt = None
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    items, total_items = await service_list_inspections(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        compliance_status=compliance_status,
        processing_status=processing_status,
        q=q,
        start_date=start_dt,
        end_date=end_dt,
        scope=scope
    )
    
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    pagination = Pagination(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    
    return InspectionListResponse(
        items=[InspectionListItem.model_validate(item) for item in items],
        pagination=pagination
    )

@router.get("/locations", response_model=LocationMarkersResponse)
async def get_inspection_locations_endpoint(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    compliance_status: Optional[str] = None,
    manufacturer_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get geo-tagged inspection locations for map markers.
    """
    from datetime import datetime
    
    start_dt = None
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
        except ValueError:
            pass
            
    end_dt = None
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
        except ValueError:
            pass
            
    is_admin = current_user.role == "ADMIN"
    officer_id = current_user.officer_profile.id if current_user.role in ["OFFICER", "ADMIN"] and getattr(current_user, 'officer_profile', None) else None
    
    from app.repositories.inspection_repository import list_inspection_locations
    items, total_items = await list_inspection_locations(
        db=db,
        user_id=current_user.id,
        officer_id=officer_id,
        is_admin=is_admin,
        page=page,
        page_size=page_size,
        compliance_status=compliance_status,
        manufacturer_name=manufacturer_name,
        start_date=start_dt,
        end_date=end_dt
    )
    
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    pagination = Pagination(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    
    from app.schemas.inspection import LocationMarker
    markers = []
    for item in items:
        markers.append(LocationMarker(
            inspection_id=item.id,
            latitude=item.latitude,
            longitude=item.longitude,
            inspection_date=item.inspection_date,
            manufacturer=item.manufacturer_name,
            compliance_status=item.compliance_status,
            processing_status=item.processing_status
        ))
        
    return LocationMarkersResponse(
        items=markers,
        pagination=pagination
    )

@router.get("/{inspection_id}", response_model=InspectionDetailResponse)
async def get_inspection_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get inspection details.
    """
    inspection = await service_get_inspection(db, current_user, inspection_id)
    return inspection

@router.post("/{inspection_id}/images", response_model=InspectionImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_inspection_image_endpoint(
    inspection_id: str,
    image: UploadFile = File(...),
    image_type: str = Form("OTHER"),
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an image for an inspection.
    """
    file_content = await image.read()
    inspection_image = await upload_inspection_image(
        db=db,
        current_user=current_user,
        inspection_id=inspection_id,
        file_content=file_content,
        original_filename=image.filename,
        content_type=image.content_type,
        image_type=image_type
    )
    return inspection_image

@router.post("/{inspection_id}/analyze", response_model=InspectionDetailResponse)
async def analyze_inspection_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger AI analysis for an inspection.
    """
    await process_inspection_analysis(
        db=db,
        inspection_id=inspection_id,
        user_id=current_user.id,
        ai_client=ai_client_instance
    )
    return await service_get_inspection(db, current_user, inspection_id)
@router.get("/{inspection_id}/violations", response_model=list[ViolationResponse])
async def get_inspection_violations_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get violations for an inspection.
    """
    inspection = await service_get_inspection(db, current_user, inspection_id)
    return inspection.violations

@router.get("/{inspection_id}/evidence", response_model=list[EvidenceResponse])
async def get_inspection_evidence_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get evidence chain for an inspection.
    """
    inspection = await service_get_inspection(db, current_user, inspection_id)
    return inspection.evidence

@router.post("/{inspection_id}/report", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_inspection_report_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a Markdown report for the given inspection from persisted data.
    """
    report = await generate_report_for_inspection(db, current_user, inspection_id)
    return report

@router.get("/{inspection_id}/report", response_model=ReportResponse)
async def get_inspection_report_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the latest generated report metadata for the given inspection.
    """
    report = await get_latest_report_for_inspection(db, current_user, inspection_id)
    return report

@router.post("/{inspection_id}/report/share", response_model=ShareResponse)
async def share_inspection_report_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate an expiring share link for the latest report.
    """
    from app.models.report import Report
    from sqlalchemy.future import select
    from fastapi import HTTPException
    
    report = await get_latest_report_for_inspection(db, current_user, inspection_id)
    
    # Generate token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Get the db report to update
    result = await db.execute(select(Report).where(Report.id == report.id))
    db_report = result.scalars().first()
    
    db_report.share_token_hash = token_hash
    db_report.share_expires_at = expires_at
    await db.commit()
    
    from app.core.config import settings
    # We construct a public UI URL, e.g., http://localhost:5173/public/reports/{raw_token}
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    share_url = f"{frontend_url}/public/reports/{raw_token}"
    
    return ShareResponse(share_url=share_url, expires_at=expires_at)

from pydantic import BaseModel

class ReviewStatusUpdate(BaseModel):
    status: str

@router.patch("/{inspection_id}/review-status", response_model=InspectionDetailResponse)
async def update_review_status_endpoint(
    inspection_id: str,
    status_update: ReviewStatusUpdate,
    current_user: User = Depends(require_officer),
    db: AsyncSession = Depends(get_db)
):
    """
    Update the review status of an inspection.
    """
    from fastapi import HTTPException
        
    inspection = await service_get_inspection(db, current_user, inspection_id)
    
    if inspection.review_status == 'LOCKED':
        raise HTTPException(status_code=400, detail="Cannot modify a LOCKED docket")
    
    valid_statuses = ["NOT_REQUIRED", "PENDING", "REVIEWED", "LOCKED", "REJECTED"]
    if status_update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid review status")
        
    inspection.review_status = status_update.status
    await db.commit()
    await db.refresh(inspection)
    
    return inspection

@router.get("/{inspection_id}/images/{image_id}/file")
async def get_inspection_image_file_endpoint(
    inspection_id: str,
    image_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Serve raw packaging image file.
    """
    import os
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
    from app.models.inspection_image import InspectionImage
    from sqlalchemy import select
    from app.core.config import settings

    await service_get_inspection(db, current_user, inspection_id)

    result = await db.execute(
        select(InspectionImage).where(
            InspectionImage.id == image_id,
            InspectionImage.inspection_id == inspection_id
        )
    )
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=404, detail="Image record not found")

    file_path = image.storage_path
    if not os.path.isabs(file_path):
        candidates = [
            os.path.join(settings.ABSOLUTE_UPLOAD_DIR, os.path.basename(file_path)),
            file_path
        ]
        for c in candidates:
            if os.path.exists(c):
                file_path = c
                break

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image file not found on disk")

    return FileResponse(file_path, media_type=image.mime_type or "image/jpeg")

@router.get("/{inspection_id}/report/download")
async def download_inspection_report_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download Markdown report file for an inspection.
    """
    import os
    from fastapi import HTTPException
    from fastapi.responses import FileResponse
    from app.models.report import Report
    from sqlalchemy import select
    from app.core.config import settings

    await service_get_inspection(db, current_user, inspection_id)
    query = select(Report).where(Report.inspection_id == inspection_id).order_by(Report.version.desc())
    result = await db.execute(query)
    report = result.scalars().first()

    if not report:
        # Auto-generate if missing
        report = await generate_report_for_inspection(db, current_user, inspection_id)

    file_path = report.report_path
    if not os.path.isabs(file_path):
        candidates = [
            os.path.join(settings.ABSOLUTE_UPLOAD_DIR, os.path.basename(file_path)),
            file_path
        ]
        for c in candidates:
            if os.path.exists(c):
                file_path = c
                break

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found on disk")

    filename = os.path.basename(file_path)
    return FileResponse(
        file_path,
        media_type="text/markdown",
        filename=filename
    )

@router.post("/{inspection_id}/notice", response_model=NoticeResponse)
async def create_notice_endpoint(
    inspection_id: str,
    data: NoticeCreate,
    current_user: User = Depends(require_officer),
    db: AsyncSession = Depends(get_db)
):
    """
    Issue a new enforcement notice for an inspection.
    """
    from fastapi import HTTPException
    
    # Verify inspection exists
    inspection = await service_get_inspection(db, current_user, inspection_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    # Fetch officer profile
    from app.models.officer import Officer
    from sqlalchemy import select
    query_officer = select(Officer).where(Officer.user_id == current_user.id)
    result_officer = await db.execute(query_officer)
    officer_profile = result_officer.scalars().first()
    if not officer_profile:
        raise HTTPException(status_code=403, detail="Officer profile not found")

    notice = EnforcementNotice(
        inspection_id=inspection_id,
        officer_id=officer_profile.id,
        status="ISSUED",
        remarks=data.remarks
    )
    db.add(notice)
    await db.commit()
    await db.refresh(notice)
    return notice

@router.get("/{inspection_id}/notices", response_model=list[NoticeResponse])
async def list_notices_endpoint(
    inspection_id: str,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List notices for an inspection.
    """
    from sqlalchemy import select
    
    await service_get_inspection(db, current_user, inspection_id)
    
    query = select(EnforcementNotice).where(EnforcementNotice.inspection_id == inspection_id)
    result = await db.execute(query)
    notices = result.scalars().all()
    return list(notices)
