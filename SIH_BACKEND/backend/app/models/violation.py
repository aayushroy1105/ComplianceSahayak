from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class Violation(Base):
    __tablename__ = "violations"
    __table_args__ = (
        CheckConstraint("status IN ('OPEN', 'REVIEWED', 'CONFIRMED', 'REJECTED', 'RESOLVED')", name="check_violation_status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    violation_code = Column(String(100), nullable=False, index=True)
    rule_id = Column(String(50), nullable=False, index=True)
    rule_version = Column(String(50))
    severity = Column(String(20))
    description = Column(Text, nullable=False)
    confidence = Column(Float)
    evidence_references = Column(JSONB, nullable=False, default=list)
    status = Column(String(20), nullable=False, default="OPEN", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="violations")
    evidence = relationship("Evidence", back_populates="violation")
    legal_references = relationship("LegalReference", back_populates="violation")
    corrective_actions = relationship("CorrectiveAction", back_populates="violation")
