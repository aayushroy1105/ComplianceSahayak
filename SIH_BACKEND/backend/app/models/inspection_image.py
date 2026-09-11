from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class InspectionImage(Base):
    __tablename__ = "inspection_images"
    __table_args__ = (
        CheckConstraint("image_type IN ('FRONT', 'BACK', 'SIDE', 'LABEL', 'MRP', 'BARCODE', 'QR', 'EVIDENCE', 'OTHER')", name="check_image_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    storage_path = Column(String(1000), nullable=False)
    image_type = Column(String(20), nullable=False, default="OTHER")
    original_filename = Column(String(500))
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    checksum = Column(String(128))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="images")
    ocr_results = relationship("OCRResult", back_populates="image")
    declarations = relationship("Declaration", back_populates="source_image")
    evidence = relationship("Evidence", back_populates="image")
