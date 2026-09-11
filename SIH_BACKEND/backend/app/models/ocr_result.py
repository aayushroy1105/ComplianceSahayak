from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    image_id = Column(UUID(as_uuid=True), ForeignKey("inspection_images.id"), nullable=False, index=True)
    full_text = Column(Text)
    confidence = Column(Float)
    ocr_model_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="ocr_results")
    image = relationship("InspectionImage", back_populates="ocr_results")
