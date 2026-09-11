from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, exc
from sqlalchemy.orm import selectinload
from typing import Optional, Tuple, Sequence
from uuid import UUID
import random
import string
from datetime import datetime, timezone
import logging
from app.models.inspection import Inspection

logger = logging.getLogger(__name__)

def generate_inspection_code() -> str:
    # Generates a code like INS-20260906-A3B4C5
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"INS-{date_str}-{random_str}"

async def create_inspection(db: AsyncSession, inspection: Inspection) -> Inspection:
    max_retries = 3
    for attempt in range(max_retries):
        if not inspection.inspection_code:
            inspection.inspection_code = generate_inspection_code()
        
        db.add(inspection)
        try:
            await db.flush()
            return inspection
        except exc.IntegrityError as e:
            await db.rollback()
            if "inspections_inspection_code_key" in str(e):
                logger.warning(f"Inspection code collision on {inspection.inspection_code}, retrying...")
                inspection.inspection_code = None # Reset for next iteration
                continue
            else:
                raise e
    raise Exception("Failed to generate a unique inspection code after max retries")

async def get_inspection(db: AsyncSession, inspection_id: UUID) -> Optional[Inspection]:
    query = (
        select(Inspection)
        .where(Inspection.id == inspection_id)
        .options(
            selectinload(Inspection.images),
            selectinload(Inspection.declarations),
            selectinload(Inspection.violations).selectinload(Inspection.violations.property.mapper.class_.corrective_actions),
            selectinload(Inspection.evidence),
            selectinload(Inspection.product),
            selectinload(Inspection.manufacturer)
        )
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_inspection_by_code(db: AsyncSession, inspection_code: str) -> Optional[Inspection]:
    query = (
        select(Inspection)
        .where(Inspection.inspection_code == inspection_code)
        .options(
            selectinload(Inspection.images),
            selectinload(Inspection.declarations),
            selectinload(Inspection.violations).selectinload(Inspection.violations.property.mapper.class_.corrective_actions),
            selectinload(Inspection.evidence),
            selectinload(Inspection.product),
            selectinload(Inspection.manufacturer)
        )
    )
    result = await db.execute(query)
    return result.scalars().first()

async def list_inspections(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    officer_id: Optional[UUID] = None,
    is_admin: bool = False,
    page: int = 1,
    page_size: int = 20,
    compliance_status: Optional[str] = None,
    processing_status: Optional[str] = None,
    q: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Tuple[Sequence[Inspection], int]:
    
    from sqlalchemy.orm import selectinload
    query = select(Inspection).options(
        selectinload(Inspection.manufacturer),
        selectinload(Inspection.violations)
    )
    
    if not is_admin:
        if officer_id:
            # Depending on requirements, officers might see all, or only their own.
            # Assuming officers can see all for now, but if restricted:
            pass
        elif user_id:
            # Regular users can only see their own inspections
            query = query.where(Inspection.user_id == user_id)
            
    if compliance_status:
        query = query.where(Inspection.compliance_status == compliance_status)
    if processing_status:
        query = query.where(Inspection.processing_status == processing_status)
    if q:
        # Search by inspection_code (case-insensitive)
        query = query.where(Inspection.inspection_code.ilike(f"%{q}%"))
    if start_date:
        query = query.where(Inspection.created_at >= start_date)
    if end_date:
        query = query.where(Inspection.created_at <= end_date)
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_items_result = await db.execute(count_query)
    total_items = total_items_result.scalar() or 0
    
    # Pagination
    offset = (page - 1) * page_size
    query = query.order_by(Inspection.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items, total_items

async def list_inspection_locations(
    db: AsyncSession,
    user_id: Optional[UUID] = None,
    officer_id: Optional[UUID] = None,
    is_admin: bool = False,
    page: int = 1,
    page_size: int = 100,
    compliance_status: Optional[str] = None,
    manufacturer_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Tuple[Sequence[Inspection], int]:
    
    from sqlalchemy.orm import selectinload
    query = select(Inspection).where(Inspection.latitude.isnot(None), Inspection.longitude.isnot(None)).options(
        selectinload(Inspection.manufacturer),
        selectinload(Inspection.violations)
    )
    
    if not is_admin:
        if officer_id:
            pass
        elif user_id:
            query = query.where(Inspection.user_id == user_id)
            
    if compliance_status:
        query = query.where(Inspection.compliance_status == compliance_status)
    
    if manufacturer_name:
        from app.models.manufacturer import Manufacturer
        query = query.join(Manufacturer, Inspection.manufacturer_id == Manufacturer.id).where(
            Manufacturer.name.ilike(f"%{manufacturer_name}%")
        )
        
    if start_date:
        query = query.where(Inspection.inspection_date >= start_date)
    if end_date:
        query = query.where(Inspection.inspection_date <= end_date)
        
    query = query.options(selectinload(Inspection.manufacturer))
        
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    query = query.order_by(Inspection.created_at.desc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    items = result.scalars().all()
    
    return items, total_items
