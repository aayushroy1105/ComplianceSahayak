from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class Declaration(Base):
    __tablename__ = "declarations"
    __table_args__ = (
        CheckConstraint("extraction_status IN ('FOUND', 'MISSING', 'UNCERTAIN', 'CONFLICTING')", name="check_extraction_status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    field_name = Column(String(100), nullable=False, index=True)
    raw_value = Column(Text)
    normalized_value = Column(JSONB)
    normalized_unit = Column(String(50))
    confidence = Column(Float, nullable=False)
    source_image_id = Column(UUID(as_uuid=True), ForeignKey("inspection_images.id"))
    bounding_box = Column(JSONB)
    extraction_status = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="declarations")
    source_image = relationship("InspectionImage", back_populates="declarations")
