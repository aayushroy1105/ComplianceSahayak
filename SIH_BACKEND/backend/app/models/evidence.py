from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), index=True)
    evidence_id_ai = Column(String(100), nullable=False, index=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey("inspection_images.id"))
    evidence_type = Column(String(50), nullable=False)
    ocr_text = Column(Text)
    bounding_box = Column(JSONB)
    declaration_reference = Column(String(100))
    rule_id = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="evidence")
    violation = relationship("Violation", back_populates="evidence")
    image = relationship("InspectionImage", back_populates="evidence")
