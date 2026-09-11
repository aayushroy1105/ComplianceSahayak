from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    inspection_id = Column(UUID(as_uuid=True), ForeignKey("inspections.id"), index=True)
    action = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    metadata_col = Column("metadata", JSONB) # using metadata_col to avoid conflict with SQLAlchemy Base.metadata

    user = relationship("User", back_populates="audit_logs")
    inspection = relationship("Inspection", back_populates="audit_logs")
