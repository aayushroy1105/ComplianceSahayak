# AI ↔ Backend API Contract

This document defines the interface between the Backend/Database layer and the AI Service.

## 1. Endpoint
**POST** `/ai/analyze`

## 2. Request Format
**Content-Type:** `multipart/form-data`

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `scan_id` | `string` | Yes | No | Unique identifier for this inspection/scan. |
| `image` | `file` | Yes | No | The package image binary file. |
| `metadata` | `json string`| No | Yes | Optional context (e.g., user-provided product category). |

*(Note: Internal testing may support base64 strings via a separate mechanism, but the primary contract relies on `multipart/form-data` file uploads).*

---

## 3. Response: Product
Identifies the type of product.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `product_name` | `string` | Yes | Yes | Extracted or inferred name of the product. |
| `product_category` | `string` | Yes | Yes | Classification category (e.g., food, cosmetic). |
| `classification_confidence` | `float` | Yes | Yes | Confidence score (0.0 to 1.0). Heuristic score in Phase 5. |
| `signals` | `array[string]` | No | Yes | Observable signals that contributed to the classification. |
| `classification_method` | `string` | No | Yes | Method used (`HEURISTIC`, `MODEL`, `MANUAL`, `UNKNOWN`). |

## 4. Response: Package Context
Identifies the packaging situation.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `package_context` | `string` | Yes | Yes | Context (e.g., retail, wholesale, imported). |
| `context_confidence` | `float` | Yes | Yes | Confidence score (0.0 to 1.0). |
| `relevant_metadata` | `object` | Yes | Yes | Any specific markers detected (e.g., "export only" text). |

## 5. Response: Declarations
Extracted structured data points from the image.

| Field | Type | Required | Nullable | Description | Allowed Values |
|---|---|---|---|---|---|
| `field_name` | `string` | Yes | No | Name of the mandatory field. | `MRP`, `NET_QUANTITY`, etc. |
| `raw_value` | `string` | Yes | Yes | The exact text extracted from the OCR. | |
| `normalized_value` | `string, number` | Yes | Yes | Standardized format (e.g., 1000, "ABC Foods"). | |
| `normalized_unit` | `string` | No | Yes | Canonical physical (e.g., "g", "ml") or monetary (e.g., "INR") unit associated with normalized_value. | |
| `confidence` | `float` | Yes | No | OCR/Extraction confidence score. | |
| `source_image_id` | `string` | Yes | Yes | Identifier for the image containing this declaration. | |
| `bounding_box` | `array[float]`| Yes | Yes | `[x, y, w, h]` coordinate bounding box. | |
| `extraction_status` | `string` | Yes | No | Status of the extraction. | `FOUND`, `MISSING`, `UNCERTAIN`, `CONFLICTING` |

## 6. Response: Applicability
Determines which legal rule IDs apply. RAG retrieves these candidate rule IDs.

| Field | Type | Required | Nullable | Description | Allowed Values |
|---|---|---|---|---|---|
| `status` | `string` | Yes | No | State of applicability determination. | `DETERMINED`, `REVIEW_REQUIRED` |
| `applicable_rule_ids` | `array[string]`| Yes | No | List of applicable rule IDs from the legal catalogue. | E.g., `["LM-001", "LM-007"]` |

## 7. Response: Compliance
The definitive compliance result.
**IMPORTANT: This status is produced by the deterministic Rule Engine. It is NOT produced by the LLM.**

| Field | Type | Required | Nullable | Description | Allowed Values |
|---|---|---|---|---|---|
| `status` | `string` | Yes | No | The final compliance status. | `COMPLIANT`, `NON_COMPLIANT`, `INCONCLUSIVE` |

## 8. Response: Violations
Details of non-compliance if the status is `NON_COMPLIANT`.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `violation_code` | `string` | Yes | No | System-defined error code (e.g., `MISSING_MRP`). |
| `rule_id` | `string` | Yes | No | Link to the specific legal rule ID. |
| `rule_version` | `string` | Yes | Yes | Version of the rule evaluated. |
| `severity` | `string` | Yes | Yes | E.g., `HIGH`, `MEDIUM`, `LOW`. |
| `description` | `string` | Yes | No | Explanation of the violation. |
| `confidence` | `float` | Yes | Yes | Confidence in this violation detection. |
| `evidence_references` | `array[string]`| Yes | No | Links to `evidence_id` items. |

## 9. Response: Legal References
The exact legal provisions retrieved by RAG and evaluated by the Rule Engine.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `rule_id` | `string` | Yes | No | Unique identifier (e.g., `LM-001`). |
| `rule_number` | `string` | Yes | Yes | Official rule number (e.g., `Rule 6(1)`). |
| `sub_rule` | `string` | Yes | Yes | Specific sub-rule. |
| `schedule` | `string` | Yes | Yes | Schedule reference. |
| `source_document` | `string` | Yes | Yes | Source PDF or act name (e.g., `1(1).pdf`). |
| `legal_version` | `string` | Yes | Yes | Version of the legal document. |
| `rule_version` | `string` | Yes | Yes | Specific version of this rule in the AI corpus. |

## 10. Response: Evidence
The digital evidence chain linking the violation back to the image.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `evidence_id` | `string` | Yes | No | Unique ID for this evidence item. |
| `image_id` | `string` | Yes | Yes | Reference to the source image. |
| `evidence_type` | `string` | Yes | No | E.g., `OCR_BOUNDING_BOX`, `MISSING_FIELD`. |
| `ocr_text` | `string` | Yes | Yes | Relevant OCR text. |
| `bounding_box` | `array[float]`| Yes | Yes | The region of the image containing the evidence. |
| `declaration_reference` | `string` | Yes | Yes | Link to a specific `field_name` from Declarations. |
| `rule_id` | `string` | Yes | Yes | Link to the evaluated rule. |
| `description` | `string` | Yes | Yes | Human-readable explanation. |

## 11. Response: Corrective Actions
Textual recommendations to fix violations.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `violation_reference` | `string` | Yes | No | Link to the specific `violation_code`. |
| `action_text` | `string` | Yes | No | LLM-generated corrective instructions. |
| `status` | `string` | Yes | Yes | Status of the recommendation. |

## 12. Response: Review
Flag indicating human intervention is needed.

| Field | Type | Required | Nullable | Description | Allowed Values (Reason) |
|---|---|---|---|---|---|
| `review_required` | `boolean` | Yes | No | True if human review is needed. | |
| `review_reason` | `string` | Yes | Yes | Machine-readable reason code. | `LOW_IMAGE_QUALITY`, `OCR_UNCERTAIN`, `APPLICABILITY_UNCERTAIN`, `CONFLICTING_INFORMATION`, `PHYSICAL_VERIFICATION_REQUIRED`, `LEGAL_CONTEXT_INSUFFICIENT`, `INSUFFICIENT_EVIDENCE` |

## 13. Response: Model Information
Versions of all pipeline stages.

| Field | Type | Required | Nullable |
|---|---|---|---|
| `ocr_version` | `string` | Yes | No |
| `classification_model_version` | `string` | Yes | No |
| `embedding_model_version` | `string` | Yes | No |
| `llm_version` | `string` | Yes | No |
| `rag_version` | `string` | Yes | No |
| `rule_engine_version` | `string` | Yes | No |
| `legal_corpus_version` | `string` | Yes | No |

## 14. Error Response
Structured error handling. Note: A pipeline failure (like `LLM_FAILURE`) should not erase valid prior results.

| Field | Type | Required | Nullable | Description |
|---|---|---|---|---|
| `success` | `boolean` | Yes | No | Always `false` on fatal API errors. |
| `error_category` | `string` | Yes | No | Standardized error code. |
| `error_detail` | `string` | Yes | No | Detailed message. |

**Allowed `error_category` Values:** 
`INVALID_REQUEST`, `INVALID_IMAGE`, `OCR_FAILURE`, `EXTRACTION_FAILURE`, `CLASSIFICATION_FAILURE`, `LEGAL_CONTEXT_INSUFFICIENT`, `RAG_FAILURE`, `RULE_ENGINE_ERROR`, `LLM_FAILURE`, `INTERNAL_ERROR`.

---

## 15. Examples

### A. Example COMPLIANT Response
```json
{
  "success": true,
  "scan_id": "DEMO-001",
  "product": {
    "product_name": "Sample Biscuits",
    "product_category": "food",
    "classification_confidence": 0.95,
    "signals": ["biscuits"],
    "classification_method": "HEURISTIC"
  },
  "package_context": {
    "package_context": "retail",
    "context_confidence": 0.98,
    "relevant_metadata": {}
  },
  "declarations": [
    {
      "field_name": "MRP",
      "raw_value": "Rs. 50",
      "normalized_value": 50.00,
      "normalized_unit": "INR",
      "confidence": 0.99,
      "source_image_id": "img1",
      "bounding_box": [10.5, 20.2, 100.0, 30.0],
      "extraction_status": "FOUND"
    }
  ],
  "applicability": {
    "status": "DETERMINED",
    "applicable_rule_ids": ["LM-001", "LM-007"]
  },
  "compliance": {
    "status": "COMPLIANT"
  },
  "violations": [],
  "corrective_actions": [],
  "legal_references": [
    {
      "rule_id": "LM-001",
      "rule_number": "Rule 1",
      "sub_rule": null,
      "schedule": null,
      "source_document": "1(1).pdf",
      "legal_version": "2011",
      "rule_version": "1.0"
    }
  ],
  "evidence": [],
  "review_required": false,
  "review_reason": null,
  "model_info": {
    "ocr_version": "v1",
    "classification_model_version": "v1",
    "embedding_model_version": "v1",
    "llm_version": "v1",
    "rag_version": "v1",
    "rule_engine_version": "v1",
    "legal_corpus_version": "v1"
  }
}
```

### B. Example NON_COMPLIANT Response
```json
{
  "success": true,
  "scan_id": "DEMO-002",
  "product": {
    "product_name": "Sample Cosmetics",
    "product_category": "cosmetic",
    "classification_confidence": 0.92
  },
  "package_context": {
    "package_context": "retail",
    "context_confidence": 0.90,
    "relevant_metadata": {}
  },
  "declarations": [
    {
      "field_name": "NET_QUANTITY",
      "raw_value": "",
      "normalized_value": null,
      "normalized_unit": null,
      "confidence": 0.0,
      "source_image_id": "img1",
      "bounding_box": null,
      "extraction_status": "MISSING"
    }
  ],
  "applicability": {
    "status": "DETERMINED",
    "applicable_rule_ids": ["LM-007", "LM-010"]
  },
  "compliance": {
    "status": "NON_COMPLIANT"
  },
  "violations": [
    {
      "violation_code": "MISSING_QUANTITY",
      "rule_id": "LM-010",
      "rule_version": "1.0",
      "severity": "HIGH",
      "description": "Net quantity is not declared on the package.",
      "confidence": 0.95,
      "evidence_references": ["EVID_001"]
    }
  ],
  "corrective_actions": [
    {
      "violation_reference": "MISSING_QUANTITY",
      "action_text": "Add a clear net quantity declaration on the principal display panel.",
      "status": "GENERATED"
    }
  ],
  "legal_references": [
    {
      "rule_id": "LM-010",
      "rule_number": "Rule 11",
      "sub_rule": "1(a)",
      "schedule": null,
      "source_document": "1(1).pdf",
      "legal_version": "2011",
      "rule_version": "1.0"
    }
  ],
  "evidence": [
    {
      "evidence_id": "EVID_001",
      "image_id": "img1",
      "evidence_type": "MISSING_FIELD",
      "ocr_text": null,
      "bounding_box": null,
      "declaration_reference": "NET_QUANTITY",
      "rule_id": "LM-010",
      "description": "System failed to find any valid quantity declaration."
    }
  ],
  "review_required": false,
  "review_reason": null,
  "model_info": {
    "ocr_version": "v1",
    "classification_model_version": "v1",
    "embedding_model_version": "v1",
    "llm_version": "v1",
    "rag_version": "v1",
    "rule_engine_version": "v1",
    "legal_corpus_version": "v1"
  }
}
```

### C. Example INCONCLUSIVE Response
```json
{
  "success": true,
  "scan_id": "DEMO-003",
  "product": {
    "product_name": null,
    "product_category": null,
    "classification_confidence": 0.30,
    "signals": [],
    "classification_method": "HEURISTIC"
  },
  "package_context": {
    "package_context": null,
    "context_confidence": 0.20,
    "relevant_metadata": {}
  },
  "declarations": [],
  "applicability": {
    "status": "REVIEW_REQUIRED",
    "applicable_rule_ids": []
  },
  "compliance": {
    "status": "INCONCLUSIVE"
  },
  "violations": [],
  "corrective_actions": [],
  "legal_references": [],
  "evidence": [],
  "review_required": true,
  "review_reason": "APPLICABILITY_UNCERTAIN",
  "model_info": {
    "ocr_version": "v1",
    "classification_model_version": "v1",
    "embedding_model_version": "v1",
    "llm_version": "v1",
    "rag_version": "v1",
    "rule_engine_version": "v1",
    "legal_corpus_version": "v1"
  }
}
```

### D. Example LOW_IMAGE_QUALITY / REVIEW_REQUIRED Response
```json
{
  "success": true,
  "scan_id": "DEMO-004",
  "product": {
    "product_name": "Sample Product",
    "product_category": "general",
    "classification_confidence": 0.90,
    "signals": [],
    "classification_method": "HEURISTIC"
  },
  "package_context": {
    "package_context": "retail",
    "context_confidence": 0.90,
    "relevant_metadata": {}
  },
  "declarations": [],
  "applicability": {
    "status": "DETERMINED",
    "applicable_rule_ids": ["LM-001"]
  },
  "compliance": {
    "status": "INCONCLUSIVE"
  },
  "violations": [],
  "corrective_actions": [],
  "legal_references": [],
  "evidence": [],
  "review_required": true,
  "review_reason": "LOW_IMAGE_QUALITY",
  "model_info": {
    "ocr_version": "v1",
    "classification_model_version": "v1",
    "embedding_model_version": "v1",
    "llm_version": "v1",
    "rag_version": "v1",
    "rule_engine_version": "v1",
    "legal_corpus_version": "v1"
  }
}
```

### E. Example LLM_FAILURE while preserving Rule Engine result
```json
{
  "success": true,
  "scan_id": "DEMO-005",
  "product": {
    "product_name": "Sample Cosmetics",
    "product_category": "cosmetic",
    "classification_confidence": 0.92
  },
  "package_context": {
    "package_context": "retail",
    "context_confidence": 0.90,
    "relevant_metadata": {}
  },
  "declarations": [
    {
      "field_name": "NET_QUANTITY",
      "raw_value": "",
      "normalized_value": null,
      "normalized_unit": null,
      "confidence": 0.0,
      "source_image_id": "img1",
      "bounding_box": null,
      "extraction_status": "MISSING"
    }
  ],
  "applicability": {
    "status": "DETERMINED",
    "applicable_rule_ids": ["LM-010"]
  },
  "compliance": {
    "status": "NON_COMPLIANT"
  },
  "violations": [
    {
      "violation_code": "MISSING_QUANTITY",
      "rule_id": "LM-010",
      "rule_version": "1.0",
      "severity": "HIGH",
      "description": "Net quantity is not declared on the package.",
      "confidence": 0.95,
      "evidence_references": []
    }
  ],
  "corrective_actions": [],
  "legal_references": [],
  "evidence": [],
  "review_required": true,
  "review_reason": "LEGAL_CONTEXT_INSUFFICIENT",
  "model_info": {
    "ocr_version": "v1",
    "classification_model_version": "v1",
    "embedding_model_version": "v1",
    "llm_version": "ERROR_TIMEOUT",
    "rag_version": "v1",
    "rule_engine_version": "v1",
    "legal_corpus_version": "v1"
  }
}
```
