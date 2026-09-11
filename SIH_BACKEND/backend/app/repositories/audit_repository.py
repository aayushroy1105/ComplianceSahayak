from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any
from uuid import UUID

async def create_audit_log(
    db: AsyncSession,
    user_id: Optional[UUID],
    action: str,
    inspection_id: UUID,
    details: Dict[str, Any]
) -> AuditLog:
    audit_log = AuditLog(
        user_id=user_id,
        inspection_id=inspection_id,
        action=action,
        metadata_col=details
    )
    db.add(audit_log)
    await db.flush() # Flush to get ID if needed, but wait for outer commit
    return audit_log
