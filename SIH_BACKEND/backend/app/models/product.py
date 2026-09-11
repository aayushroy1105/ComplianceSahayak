from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manufacturer_id = Column(UUID(as_uuid=True), ForeignKey("manufacturers.id"), index=True)
    product_name = Column(String(500), nullable=False)
    category = Column(String(100), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    manufacturer = relationship("Manufacturer", back_populates="products")
    inspections = relationship("Inspection", back_populates="product")
