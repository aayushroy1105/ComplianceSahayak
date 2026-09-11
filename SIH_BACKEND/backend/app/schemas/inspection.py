from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any, Union

class InspectionImageResponse(BaseModel):
    id: UUID
    image_type: str
    original_filename: Optional[str]
    mime_type: str
    file_size: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InspectionCreateRequest(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    location_text: Optional[str] = None
    inspection_date: Optional[datetime] = None
    officer_notes: Optional[str] = None
    product_id: Optional[UUID] = None
    manufacturer_id: Optional[UUID] = None

class InspectionCreateResponse(BaseModel):
    id: UUID
    inspection_code: str
    processing_status: str
    compliance_status: Optional[str]
    review_status: str
    image: Optional[InspectionImageResponse] = None
    latitude: Optional[float]
    longitude: Optional[float]
    location_text: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InspectionListItem(BaseModel):
    id: UUID
    inspection_code: str
    processing_status: str
    compliance_status: Optional[str]
    review_status: str
    product_name_ai: Optional[str] = None
    product_category_ai: Optional[str] = None
    signals: Optional[List[str]] = None
    classification_method: Optional[str] = None
    manufacturer_name: Optional[str] = None
    violation_count: int = 0
    latitude: Optional[float]
    longitude: Optional[float]
    location_text: Optional[str]
    inspection_date: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class Pagination(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class InspectionListResponse(BaseModel):
    items: List[InspectionListItem]
    pagination: Pagination

class LocationMarker(BaseModel):
    inspection_id: UUID
    latitude: float
    longitude: float
    inspection_date: Optional[datetime]
    manufacturer: Optional[str]
    compliance_status: Optional[str]
    processing_status: str

    model_config = ConfigDict(from_attributes=True)

class LocationMarkersResponse(BaseModel):
    items: List[LocationMarker]
    pagination: Pagination

class DeclarationResponse(BaseModel):
    id: UUID
    field_name: str
    raw_value: Optional[str]
    normalized_value: Union[str, float, int, None]
    normalized_unit: Optional[str] = None
    confidence: float
    extraction_status: str
    bounding_box: Optional[List[float]] = None
    
    model_config = ConfigDict(from_attributes=True)

class CorrectiveActionResponse(BaseModel):
    id: UUID
    violation_reference: str
    action_text: str
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class ViolationResponse(BaseModel):
    id: UUID
    violation_code: str
    rule_id: str
    rule_version: Optional[str] = None
    severity: Optional[str]
    description: str
    confidence: Optional[float]
    evidence_references: List[str]
    status: str
    corrective_actions: List[CorrectiveActionResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class EvidenceResponse(BaseModel):
    id: UUID
    evidence_id_ai: str
    evidence_type: str
    ocr_text: Optional[str]
    bounding_box: Optional[List[float]] = None
    declaration_reference: Optional[str]
    rule_id: Optional[str]
    description: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

    # Additional schemas for detailed GET response (omitted some parts for brevity in this mock)
class InspectionDetailResponse(BaseModel):
    id: UUID
    inspection_code: str
    processing_status: str
    compliance_status: Optional[str]
    review_status: str
    review_required: Optional[bool]
    review_reason: Optional[str]
    
    latitude: Optional[float]
    longitude: Optional[float]
    location_text: Optional[str]
    inspection_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    product_name_ai: Optional[str] = None
    product_category_ai: Optional[str] = None
    signals: Optional[List[str]] = None
    classification_method: Optional[str] = None
    
    images: List[InspectionImageResponse] = []
    declarations: List[DeclarationResponse] = []
    violations: List[ViolationResponse] = []
    evidence: List[EvidenceResponse] = []

    model_config = ConfigDict(from_attributes=True)
