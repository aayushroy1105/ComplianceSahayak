from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.schemas.inspection import Pagination

class ProductResponse(BaseModel):
    id: UUID
    product_name: str
    category: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ManufacturerResponse(BaseModel):
    id: UUID
    name: str
    normalized_name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ManufacturerDetailResponse(ManufacturerResponse):
    products: List[ProductResponse] = []
    
class ManufacturerListResponse(BaseModel):
    items: List[ManufacturerResponse]
    pagination: Pagination

class ManufacturerHistoryItem(BaseModel):
    id: UUID
    inspection_code: str
    inspection_date: Optional[datetime]
    processing_status: str
    compliance_status: Optional[str]
    product_name_ai: Optional[str]
    violation_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ManufacturerHistoryResponse(BaseModel):
    items: List[ManufacturerHistoryItem]
    pagination: Pagination
