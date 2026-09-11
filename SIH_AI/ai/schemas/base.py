from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Union, Any

class Product(BaseModel):
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    classification_confidence: Optional[float] = None
    signals: Optional[List[str]] = None
    classification_method: Optional[str] = None

class PackageContext(BaseModel):
    package_context: Optional[str] = None
    context_confidence: Optional[float] = None
    relevant_metadata: Optional[Dict[str, Any]] = None

class Declaration(BaseModel):
    field_name: str
    raw_value: Optional[str] = None
    normalized_value: Optional[Union[str, float, int]] = None
    normalized_unit: Optional[str] = None
    confidence: float
    source_image_id: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    extraction_status: str

class Applicability(BaseModel):
    status: str
    applicable_rule_ids: List[str] = []

class Compliance(BaseModel):
    status: str

class Violation(BaseModel):
    violation_code: str
    rule_id: str
    rule_version: Optional[str] = None
    severity: Optional[str] = None
    description: str
    confidence: Optional[float] = None
    evidence_references: List[str] = []

class CorrectiveAction(BaseModel):
    violation_reference: str
    action_text: str
    status: Optional[str] = None

class LegalReference(BaseModel):
    rule_id: str
    rule_number: Optional[str] = None
    sub_rule: Optional[str] = None
    schedule: Optional[str] = None
    source_document: Optional[str] = None
    legal_version: Optional[str] = None
    rule_version: Optional[str] = None

class Evidence(BaseModel):
    evidence_id: str
    image_id: Optional[str] = None
    evidence_type: str
    ocr_text: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    declaration_reference: Optional[str] = None
    rule_id: Optional[str] = None
    description: Optional[str] = None

class ModelInfo(BaseModel):
    ocr_version: str
    classification_model_version: str
    embedding_model_version: str
    llm_version: str
    rag_version: str
    rule_engine_version: str
    legal_corpus_version: str

# Note: The request model is no longer used directly in the route for validation since we use multipart/form-data.
# We keep it as a logical representation if needed.
class AnalyzeRequest(BaseModel):
    scan_id: str
    metadata: Optional[Dict[str, Any]] = None

class AnalyzeResponse(BaseModel):
    success: bool
    scan_id: str
    product: Product
    package_context: PackageContext
    declarations: List[Declaration]
    applicability: Applicability
    compliance: Compliance
    violations: List[Violation]
    corrective_actions: List[CorrectiveAction]
    legal_references: List[LegalReference]
    evidence: List[Evidence]
    review_required: bool
    review_reason: Optional[str] = None
    model_info: ModelInfo
    raw_ocr_blocks: Optional[List[Dict[str, Any]]] = None
