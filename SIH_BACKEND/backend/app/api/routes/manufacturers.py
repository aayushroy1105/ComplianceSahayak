from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math
from uuid import UUID

from app.api.dependencies import get_db, require_user
from app.models.user import User
from app.schemas.manufacturer import (
    ManufacturerListResponse,
    ManufacturerDetailResponse,
    ManufacturerResponse,
    ManufacturerHistoryResponse,
    ManufacturerHistoryItem
)
from app.schemas.inspection import Pagination
from app.repositories.manufacturer_repository import (
    list_manufacturers,
    get_manufacturer,
    get_manufacturer_history
)

router = APIRouter()

@router.get("", response_model=ManufacturerListResponse)
async def list_manufacturers_endpoint(
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    items, total_items = await list_manufacturers(db, search, page, page_size)
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    pagination = Pagination(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    
    return ManufacturerListResponse(
        items=[ManufacturerResponse.model_validate(item) for item in items],
        pagination=pagination
    )

@router.get("/{manufacturer_id}", response_model=ManufacturerDetailResponse)
async def get_manufacturer_endpoint(
    manufacturer_id: UUID,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    manufacturer = await get_manufacturer(db, manufacturer_id)
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
    return manufacturer

@router.get("/{manufacturer_id}/history", response_model=ManufacturerHistoryResponse)
async def get_manufacturer_history_endpoint(
    manufacturer_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify existence
    manufacturer = await get_manufacturer(db, manufacturer_id)
    if not manufacturer:
        raise HTTPException(status_code=404, detail="Manufacturer not found")
        
    items, total_items = await get_manufacturer_history(db, manufacturer_id, page, page_size)
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 1
    
    pagination = Pagination(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages
    )
    
    history_items = []
    for inspection in items:
        history_items.append(
            ManufacturerHistoryItem(
                id=inspection.id,
                inspection_code=inspection.inspection_code,
                inspection_date=inspection.inspection_date,
                processing_status=inspection.processing_status,
                compliance_status=inspection.compliance_status,
                product_name_ai=getattr(inspection, "product_name_ai", None),
                violation_count=len(inspection.violations),
                created_at=inspection.created_at
            )
        )
        
    return ManufacturerHistoryResponse(
        items=history_items,
        pagination=pagination
    )
