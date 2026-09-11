from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from uuid import UUID
from datetime import datetime
from typing import Optional, Tuple, Sequence
from app.models.inspection import Inspection
from app.models.user import User
from app.schemas.inspection import InspectionCreateRequest
from app.repositories.inspection_repository import create_inspection as repo_create_inspection, list_inspections as repo_list_inspections, get_inspection as repo_get_inspection, get_inspection_by_code
from app.repositories.audit_repository import create_audit_log
from app.models.inspection_image import InspectionImage
from app.services.storage_service import storage_service
from app.services.image_service import validate_image_file
import hashlib

async def create_inspection(db: AsyncSession, current_user: User, data: InspectionCreateRequest) -> Inspection:
    # Validate location
    if data.latitude is not None and not (-90 <= data.latitude <= 90):
        raise HTTPException(status_code=422, detail="Latitude must be between -90 and 90")
    if data.longitude is not None and not (-180 <= data.longitude <= 180):
        raise HTTPException(status_code=422, detail="Longitude must be between -180 and 180")

    # Construct the base Inspection entity
    inspection = Inspection(
        user_id=current_user.id,
        officer_id=current_user.officer_profile.id if current_user.role in ["OFFICER", "ADMIN"] and getattr(current_user, 'officer_profile', None) else None,
        product_id=data.product_id,
        manufacturer_id=data.manufacturer_id,
        processing_status="PENDING",
        review_status="NOT_REQUIRED",
        latitude=data.latitude,
        longitude=data.longitude,
        location_text=data.location_text,
        officer_notes=data.officer_notes,
        inspection_date=data.inspection_date or datetime.utcnow()
    )

    created_inspection = await repo_create_inspection(db, inspection)
    
    # Create audit log within the same transaction (which happens in the route via db.commit)
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action="INSPECTION_CREATED",
        inspection_id=created_inspection.id,
        details={"inspection_code": created_inspection.inspection_code, "latitude": data.latitude, "longitude": data.longitude}
    )

    return created_inspection

async def get_inspection(db: AsyncSession, current_user: User, inspection_id: str) -> Inspection:
    # inspection_id can be UUID or code
    try:
        parsed_uuid = UUID(inspection_id)
        inspection = await repo_get_inspection(db, parsed_uuid)
    except ValueError:
        inspection = await get_inspection_by_code(db, inspection_id)
        
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    # Enforce authorization
    if current_user.role == "USER" and inspection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden: You do not have access to this inspection")
        
    return inspection

async def list_inspections(
    db: AsyncSession,
    current_user: User,
    page: int = 1,
    page_size: int = 20,
    compliance_status: Optional[str] = None,
    processing_status: Optional[str] = None,
    q: Optional[str] = None,
    start_date=None,
    end_date=None,
    scope: Optional[str] = None
):
    is_admin = current_user.role == "ADMIN"
    officer_id = current_user.officer_profile.id if current_user.role in ["OFFICER", "ADMIN"] and getattr(current_user, 'officer_profile', None) else None
    user_id = current_user.id
    
    # Strictly enforce user scoping if explicitly requested
    if scope == "user":
        is_admin = False
        officer_id = None

    return await repo_list_inspections(
        db=db,
        user_id=user_id,
        officer_id=officer_id,
        is_admin=is_admin,
        page=page,
        page_size=page_size,
        compliance_status=compliance_status,
        processing_status=processing_status,
        q=q,
        start_date=start_date,
        end_date=end_date
    )

async def upload_inspection_image(
    db: AsyncSession,
    current_user: User,
    inspection_id: str,
    file_content: bytes,
    original_filename: str,
    content_type: str,
    image_type: str = "OTHER"
) -> InspectionImage:
    # 1. Authorize & Load Inspection
    inspection = await get_inspection(db, current_user, inspection_id)
    
    if inspection.review_status == "LOCKED":
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Cannot upload images to a locked inspection")
    
    # 2. Validate file
    metadata = validate_image_file(file_content, original_filename, content_type)
    
    # Checksum for integrity
    checksum = hashlib.sha256(file_content).hexdigest()
    
    # 3. Write storage
    storage_path = await storage_service.save_file(file_content, original_filename)
    
    # 4. Create DB record
    inspection_image = InspectionImage(
        inspection_id=inspection.id,
        storage_path=storage_path,
        image_type=image_type,
        original_filename=original_filename,
        mime_type=content_type,
        file_size=metadata["file_size"],
        checksum=checksum
    )
    
    try:
        db.add(inspection_image)
        await db.commit()
        await db.refresh(inspection_image)
        
        # 5. Audit
        await create_audit_log(
            db=db,
            user_id=current_user.id,
            action="IMAGE_UPLOADED",
            inspection_id=inspection.id,
            details={
                "image_id": str(inspection_image.id),
                "image_type": image_type,
                "file_size": metadata["file_size"],
                "mime_type": content_type
            }
        )
        await db.commit()
        return inspection_image
    except Exception as e:
        await db.rollback()
        # Rollback storage
        await storage_service.delete_file(storage_path)
        raise e

