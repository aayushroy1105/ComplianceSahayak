from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), index=True)
    violation_reference = Column(String(100), nullable=False)
    action_text = Column(Text, nullable=False)
    status = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="corrective_actions")
    violation = relationship("Violation", back_populates="corrective_actions")
