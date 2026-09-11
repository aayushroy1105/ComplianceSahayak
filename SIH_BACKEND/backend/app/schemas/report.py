from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

class ReportResponse(BaseModel):
    id: UUID
    inspection_id: UUID
    report_path: str
    report_type: str
    version: int
    generated_by: Optional[UUID] = None
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ShareResponse(BaseModel):
    share_url: str
    expires_at: datetime

