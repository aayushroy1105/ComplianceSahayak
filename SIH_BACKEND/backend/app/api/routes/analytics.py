from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db, require_user
from app.models.user import User
from app.schemas.analytics import AnalyticsRepeatOffendersResponse, ManufacturerAnalytics
from app.repositories.analytics_repository import get_repeat_offender_analytics

router = APIRouter()

@router.get("/repeat-offenders", response_model=AnalyticsRepeatOffendersResponse)
async def repeat_offenders_analytics_endpoint(
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db)
):
    # Officer/Admin visibility check
    if current_user.role not in ["OFFICER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Forbidden: Requires OFFICER or ADMIN role")
        
    analytics_data = await get_repeat_offender_analytics(db)
    
    # We can validate using the schema
    offenders = [ManufacturerAnalytics(**data) for data in analytics_data]
    return AnalyticsRepeatOffendersResponse(offenders=offenders)
