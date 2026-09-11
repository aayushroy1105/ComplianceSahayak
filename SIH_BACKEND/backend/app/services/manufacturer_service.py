from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import re

from app.models.manufacturer import Manufacturer

def normalize_manufacturer_name(name: str) -> str:
    if not name:
        return ""
    # 1. Lowercase
    normalized = name.lower()
    # 2. Replace punctuation with space
    normalized = re.sub(r'[^\w\s]', ' ', normalized)
    # 3. Squash whitespace
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    return normalized

async def get_or_create_manufacturer(db: AsyncSession, name: str) -> Manufacturer:
    normalized = normalize_manufacturer_name(name)
    if not normalized:
        normalized = "unknown"
    
    # Try fetch
    result = await db.execute(select(Manufacturer).where(Manufacturer.normalized_name == normalized))
    m = result.scalars().first()
    
    if m:
        return m
        
    # Create new
    m = Manufacturer(
        name=name.strip() or "Unknown",
        normalized_name=normalized
    )
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return m
