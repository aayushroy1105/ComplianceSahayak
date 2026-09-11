from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class EnforcementNotice(Base):
    __tablename__ = "enforcement_notices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    officer_id = Column(UUID(as_uuid=True), ForeignKey("officers.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="ISSUED")
    remarks = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    inspection = relationship("Inspection", back_populates="notices")
    officer = relationship("Officer")
