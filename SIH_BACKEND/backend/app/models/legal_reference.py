from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class LegalReference(Base):
    __tablename__ = "legal_references"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), index=True)
    rule_id = Column(String(50), nullable=False, index=True)
    rule_number = Column(String(100))
    sub_rule = Column(String(100))
    schedule = Column(String(100))
    source_document = Column(String(255))
    legal_version = Column(String(50))
    rule_version = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="legal_references")
    violation = relationship("Violation", back_populates="legal_references")
