from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class ViolationFrequency(BaseModel):
    violation_code: str
    count: int

class ManufacturerAnalytics(BaseModel):
    manufacturer_id: UUID
    manufacturer_name: str
    total_inspections: int
    total_violations: int
    repeat_violation_count: int
    top_violation_codes: List[str]
    latest_inspection: Optional[datetime]
    compliance_summary: str  # e.g., "POOR", "AVERAGE", "GOOD" based on ratio
    
    model_config = ConfigDict(from_attributes=True)

class AnalyticsRepeatOffendersResponse(BaseModel):
    offenders: List[ManufacturerAnalytics]
