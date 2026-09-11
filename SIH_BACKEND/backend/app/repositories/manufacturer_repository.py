from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from uuid import UUID
from typing import Tuple, Sequence

from app.models.manufacturer import Manufacturer
from app.models.inspection import Inspection

async def list_manufacturers(
    db: AsyncSession,
    search: str = None,
    page: int = 1,
    page_size: int = 20
) -> Tuple[Sequence[Manufacturer], int]:
    query = select(Manufacturer)
    
    if search:
        search_term = f"%{search.lower()}%"
        query = query.where(
            or_(
                func.lower(Manufacturer.name).like(search_term),
                Manufacturer.normalized_name.like(search_term)
            )
        )
        
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    query = query.order_by(Manufacturer.name.asc()).offset(offset).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all(), total_items

async def get_manufacturer(db: AsyncSession, manufacturer_id: UUID) -> Manufacturer:
    query = (
        select(Manufacturer)
        .where(Manufacturer.id == manufacturer_id)
        .options(selectinload(Manufacturer.products))
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_manufacturer_history(
    db: AsyncSession,
    manufacturer_id: UUID,
    page: int = 1,
    page_size: int = 20
):
    query = select(Inspection).where(Inspection.manufacturer_id == manufacturer_id)
    
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar() or 0
    
    offset = (page - 1) * page_size
    # We want inspection_code, inspection_date, processing_status, compliance_status, product_name_ai
    # And we also want violation_count.
    # It's better to eager load violations to count them, or do a joined query.
    # We will use selectinload on violations to count them in Python, since pagination is small (20 records).
    query = (
        query
        .options(selectinload(Inspection.violations))
        .order_by(Inspection.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    
    result = await db.execute(query)
    inspections = result.scalars().all()
    
    # We will transform them into the ManufacturerHistoryItem format in the route.
    return inspections, total_items
