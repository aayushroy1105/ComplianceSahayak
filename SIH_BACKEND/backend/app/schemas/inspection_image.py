from pydantic import BaseModel, ConfigDict, computed_field
from uuid import UUID
from datetime import datetime
from typing import Optional

class InspectionImageResponse(BaseModel):
    id: UUID
    inspection_id: UUID
    image_type: str
    mime_type: str
    file_size: int
    original_filename: Optional[str]
    uploaded_at: datetime
    checksum: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def image_url(self) -> str:
        return f"/api/v1/inspections/{self.inspection_id}/images/{self.id}/file"
