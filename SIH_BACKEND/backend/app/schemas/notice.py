from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class NoticeCreate(BaseModel):
    remarks: Optional[str] = None

class NoticeResponse(BaseModel):
    id: UUID
    inspection_id: UUID
    officer_id: UUID
    status: str
    remarks: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
