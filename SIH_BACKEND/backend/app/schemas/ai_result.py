from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict, Union

class ModelInfo(BaseModel):
    ocr_version: str = "v1"
    classification_model_version: str = "v1"
    embedding_model_version: str = "v1"
    llm_version: str = "v1"
    rag_version: str = "v1"
    rule_engine_version: str = "v1"
    legal_corpus_version: str = "v1"

class AIProductClassification(BaseModel):
    product_name: Optional[str] = None
    product_category: Optional[str] = None
    classification_confidence: Optional[float] = None
    signals: Optional[List[str]] = None
    classification_method: Optional[str] = None

class AIPackageContext(BaseModel):
    package_context: Optional[str] = None
    context_confidence: Optional[float] = None
    relevant_metadata: Optional[Dict[str, Any]] = {}

class AIDeclaration(BaseModel):
    field_name: str
    raw_value: Optional[str] = None
    normalized_value: Union[str, float, int, None] = None
    normalized_unit: Optional[str] = None
    confidence: float
    source_image_id: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    extraction_status: str

class AIApplicability(BaseModel):
    status: str
    applicable_rule_ids: List[str]

class AICompliance(BaseModel):
    status: str

class AILegalReference(BaseModel):
    rule_id: str
    rule_number: Optional[str] = None
    sub_rule: Optional[str] = None
    schedule: Optional[str] = None
    source_document: Optional[str] = None
    legal_version: Optional[str] = None
    rule_version: Optional[str] = None

class AICorrectiveAction(BaseModel):
    violation_reference: str
    action_text: str
    status: str = "GENERATED"

class AIViolation(BaseModel):
    violation_code: str
    rule_id: str
    rule_version: Optional[str] = None
    severity: Optional[str] = None
    description: str
    confidence: Optional[float] = None
    evidence_references: List[str]

class AIEvidence(BaseModel):
    evidence_id: str
    image_id: Optional[str] = None
    evidence_type: str
    ocr_text: Optional[str] = None
    bounding_box: Optional[List[float]] = None
    declaration_reference: Optional[str] = None
    rule_id: Optional[str] = None
    description: Optional[str] = None

class AIAnalyzeResponse(BaseModel):
    success: bool
    scan_id: str
    product: AIProductClassification
    package_context: AIPackageContext
    declarations: List[AIDeclaration]
    applicability: AIApplicability
    compliance: AICompliance
    violations: List[AIViolation]
    corrective_actions: List[AICorrectiveAction]
    legal_references: List[AILegalReference]
    evidence: List[AIEvidence]
    review_required: bool
    review_reason: Optional[str] = None
    model_info: ModelInfo
    raw_ocr_blocks: Optional[List[Dict[str, Any]]] = None

class AIErrorResponse(BaseModel):
    success: bool
    error_category: str
    error_detail: str
