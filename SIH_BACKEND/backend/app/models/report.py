from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), nullable=False, index=True)
    report_path = Column(String(1000), nullable=False)
    report_type = Column(String(50), nullable=False, default="INSPECTION")
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    version = Column(Integer, nullable=False, default=1)
    generated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    share_token_hash = Column(String(255), nullable=True)
    share_expires_at = Column(DateTime(timezone=True), nullable=True)

    inspection = relationship("Inspection", back_populates="reports")
    generator = relationship("User")
