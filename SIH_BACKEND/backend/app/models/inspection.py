from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, DOUBLE_PRECISION
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.base import Base

class Inspection(Base):
    __tablename__ = "inspections"
    __table_args__ = (
        CheckConstraint("processing_status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED')", name="check_processing_status"),
        CheckConstraint("compliance_status IN ('COMPLIANT', 'NON_COMPLIANT', 'INCONCLUSIVE')", name="check_compliance_status"),
        CheckConstraint("review_status IN ('NOT_REQUIRED', 'PENDING', 'REVIEWED', 'LOCKED', 'REJECTED')", name="check_review_status"),
        CheckConstraint("review_reason IN ('LOW_IMAGE_QUALITY', 'OCR_UNCERTAIN', 'APPLICABILITY_UNCERTAIN', 'CONFLICTING_INFORMATION', 'PHYSICAL_VERIFICATION_REQUIRED', 'LEGAL_CONTEXT_INSUFFICIENT', 'INSUFFICIENT_EVIDENCE')", name="check_review_reason"),
        CheckConstraint("applicability_status IN ('DETERMINED', 'REVIEW_REQUIRED')", name="check_applicability_status"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inspection_code = Column(String(20), unique=True, index=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    officer_id = Column(UUID(as_uuid=True), ForeignKey("officers.id"), index=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    manufacturer_id = Column(UUID(as_uuid=True), ForeignKey("manufacturers.id"), index=True)
    
    # Status Fields
    processing_status = Column(String(20), nullable=False, default="PENDING", index=True)
    compliance_status = Column(String(20), index=True)
    review_status = Column(String(20), nullable=False, default="NOT_REQUIRED")
    review_required = Column(Boolean)
    review_reason = Column(String(50))
    
    # Applicability
    applicability_status = Column(String(20))
    applicable_rule_ids = Column(JSONB)
    
    # Product Classification
    product_name_ai = Column(String(500))
    product_category_ai = Column(String(100))
    classification_confidence = Column(Float)
    signals = Column(JSONB)
    classification_method = Column(String(50))
    
    # Package Context
    package_context = Column(String(100))
    context_confidence = Column(Float)
    relevant_metadata = Column(JSONB)
    
    # Location
    latitude = Column(DOUBLE_PRECISION)
    longitude = Column(DOUBLE_PRECISION)
    location_text = Column(String(500))
    
    # Model Versions
    ocr_version = Column(String(50))
    classification_model_version = Column(String(50))
    embedding_model_version = Column(String(50))
    llm_version = Column(String(50))
    rag_version = Column(String(50))
    rule_engine_version = Column(String(50))
    legal_corpus_version = Column(String(50))
    
    # Officer Notes
    officer_notes = Column(Text)
    
    # Timestamps
    inspection_date = Column(DateTime(timezone=True), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="inspections")
    officer = relationship("Officer", back_populates="inspections")
    product = relationship("Product", back_populates="inspections")
    manufacturer = relationship("Manufacturer", back_populates="inspections")
    
    @property
    def manufacturer_name(self) -> Optional[str]:
        return self.manufacturer.name if self.manufacturer else "Unknown Manufacturer"
    
    images = relationship("InspectionImage", back_populates="inspection")
    ocr_results = relationship("OCRResult", back_populates="inspection")
    declarations = relationship("Declaration", back_populates="inspection")
    violations = relationship("Violation", back_populates="inspection")
    
    @property
    def violation_count(self) -> int:
        return len(self.violations) if self.violations else 0

    evidence = relationship("Evidence", back_populates="inspection")
    legal_references = relationship("LegalReference", back_populates="inspection")
    corrective_actions = relationship("CorrectiveAction", back_populates="inspection")
    notices = relationship("EnforcementNotice", back_populates="inspection", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="inspection")
    audit_logs = relationship("AuditLog", back_populates="inspection")
