# Database Contract

**Project:** SIH 2026 — PS 26034  
**Version:** 1.0  
**Status:** DESIGN FREEZE  
**Canonical AI Contract:** [AI_API_CONTRACT.md](../AI_API_CONTRACT.md)

This document defines the final relational database design for the Backend + Database layer.

PostgreSQL is the primary application database.

---

## Design Principles

1. Every inspection receives a unique human-readable ID (`INS-YYYY-NNNNNN`).
2. Three independent status concepts: `processing_status`, `compliance_status`, `review_status`.
3. Evidence chain is preserved relationally: Inspection → Image → OCR → Declaration → Violation → Evidence → Legal Reference → Corrective Action.
4. JSON/JSONB is used only for structured metadata that does not require independent relational querying (e.g., bounding boxes, relevant_metadata, applicable_rule_ids).
5. Backend stores AI results verbatim — it does not invent legal rules, compliance decisions, or applicability.
6. All 7 model/version fields from the AI contract are persisted.
7. Foreign keys enforce referential integrity.
8. Timestamps use `TIMESTAMPTZ`.

---

## Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ INSPECTIONS : "creates"
    USERS ||--o| OFFICERS : "extends"
    USERS ||--o{ AUDIT_LOGS : "performs"

    OFFICERS ||--o{ INSPECTIONS : "conducts"

    MANUFACTURERS ||--o{ PRODUCTS : "produces"
    MANUFACTURERS ||--o{ INSPECTIONS : "inspected as"

    PRODUCTS ||--o{ INSPECTIONS : "inspected"

    INSPECTIONS ||--o{ INSPECTION_IMAGES : "contains"
    INSPECTIONS ||--o{ OCR_RESULTS : "produces"
    INSPECTIONS ||--o{ DECLARATIONS : "extracts"
    INSPECTIONS ||--o{ VIOLATIONS : "detects"
    INSPECTIONS ||--o{ EVIDENCE : "links"
    INSPECTIONS ||--o{ LEGAL_REFERENCES : "references"
    INSPECTIONS ||--o{ CORRECTIVE_ACTIONS : "suggests"
    INSPECTIONS ||--o| REPORTS : "generates"
    INSPECTIONS ||--o{ AUDIT_LOGS : "tracks"

    INSPECTION_IMAGES ||--o{ OCR_RESULTS : "scanned by"
    INSPECTION_IMAGES ||--o{ DECLARATIONS : "source of"
    INSPECTION_IMAGES ||--o{ EVIDENCE : "source of"

    VIOLATIONS ||--o{ EVIDENCE : "supported by"
    VIOLATIONS ||--o{ LEGAL_REFERENCES : "governed by"
    VIOLATIONS ||--o{ CORRECTIVE_ACTIONS : "addressed by"

    USERS {
        uuid id PK
        varchar name
        varchar email UK
        varchar password_hash
        enum role
        timestamptz created_at
        timestamptz updated_at
    }

    OFFICERS {
        uuid id PK
        uuid user_id FK_UK
        varchar badge_number
        varchar department
        varchar jurisdiction
        timestamptz created_at
        timestamptz updated_at
    }

    MANUFACTURERS {
        uuid id PK
        varchar name
        varchar normalized_name UK
        timestamptz created_at
        timestamptz updated_at
    }

    PRODUCTS {
        uuid id PK
        uuid manufacturer_id FK
        varchar product_name
        varchar category
        timestamptz created_at
        timestamptz updated_at
    }

    INSPECTIONS {
        uuid id PK
        varchar inspection_code UK
        uuid user_id FK
        uuid officer_id FK
        uuid product_id FK
        uuid manufacturer_id FK
        enum processing_status
        enum compliance_status
        enum review_status
        varchar review_reason
        boolean review_required
        varchar applicability_status
        jsonb applicable_rule_ids
        varchar product_name_ai
        varchar product_category_ai
        float classification_confidence
        varchar package_context
        float context_confidence
        jsonb relevant_metadata
        float latitude
        float longitude
        varchar location_text
        varchar ocr_version
        varchar classification_model_version
        varchar embedding_model_version
        varchar llm_version
        varchar rag_version
        varchar rule_engine_version
        varchar legal_corpus_version
        timestamptz inspection_date
        timestamptz created_at
        timestamptz updated_at
    }

    INSPECTION_IMAGES {
        uuid id PK
        uuid inspection_id FK
        varchar storage_path
        enum image_type
        varchar original_filename
        varchar mime_type
        integer file_size
        varchar checksum
        timestamptz uploaded_at
    }

    OCR_RESULTS {
        uuid id PK
        uuid inspection_id FK
        uuid image_id FK
        text full_text
        float confidence
        varchar ocr_model_version
        timestamptz created_at
    }

    DECLARATIONS {
        uuid id PK
        uuid inspection_id FK
        varchar field_name
        text raw_value
        text normalized_value
        float confidence
        uuid source_image_id FK
        jsonb bounding_box
        enum extraction_status
        timestamptz created_at
    }

    VIOLATIONS {
        uuid id PK
        uuid inspection_id FK
        varchar violation_code
        varchar rule_id
        varchar rule_version
        varchar severity
        text description
        float confidence
        jsonb evidence_references
        enum status
        timestamptz created_at
        timestamptz updated_at
    }

    EVIDENCE {
        uuid id PK
        uuid inspection_id FK
        uuid violation_id FK
        varchar evidence_id_ai
        uuid image_id FK
        varchar evidence_type
        text ocr_text
        jsonb bounding_box
        varchar declaration_reference
        varchar rule_id
        text description
        timestamptz created_at
    }

    LEGAL_REFERENCES {
        uuid id PK
        uuid inspection_id FK
        uuid violation_id FK
        varchar rule_id
        varchar rule_number
        varchar sub_rule
        varchar schedule
        varchar source_document
        varchar legal_version
        varchar rule_version
        timestamptz created_at
    }

    CORRECTIVE_ACTIONS {
        uuid id PK
        uuid inspection_id FK
        uuid violation_id FK
        varchar violation_reference
        text action_text
        varchar status
        timestamptz created_at
    }

    REPORTS {
        uuid id PK
        uuid inspection_id FK
        varchar report_path
        varchar report_type
        uuid generated_by FK
        integer version
        timestamptz generated_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        uuid inspection_id FK
        varchar action
        timestamptz timestamp
        jsonb metadata
    }
```

---

## 1. USERS

**Purpose:** Stores all system users — both regular users and officers.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `name` | `VARCHAR(255)` | No | — | — |
| `email` | `VARCHAR(255)` | No | — | **UNIQUE** |
| `password_hash` | `VARCHAR(255)` | No | — | — |
| `role` | `VARCHAR(20)` | No | `'USER'` | CHECK: `USER`, `OFFICER`, `ADMIN` |
| `is_active` | `BOOLEAN` | No | `true` | — |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | — |
| `updated_at` | `TIMESTAMPTZ` | No | `NOW()` | — |

**Indexes:**
- `ix_users_email` on `email` (UNIQUE)
- `ix_users_role` on `role`

**Relationships:**
- One-to-many → `inspections` (as creator)
- One-to-one → `officers` (optional extension)
- One-to-many → `audit_logs`

---

## 2. OFFICERS

**Purpose:** Extends a user with officer-specific metadata. An officer IS a user with `role = 'OFFICER'`.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `user_id` | `UUID` | No | — | **UNIQUE**, FK → `users.id` |
| `badge_number` | `VARCHAR(100)` | Yes | — | — |
| `department` | `VARCHAR(255)` | Yes | — | — |
| `jurisdiction` | `VARCHAR(255)` | Yes | — | — |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | — |
| `updated_at` | `TIMESTAMPTZ` | No | `NOW()` | — |

**Indexes:**
- `ix_officers_user_id` on `user_id` (UNIQUE)
- `ix_officers_badge_number` on `badge_number`

**Relationships:**
- Many-to-one → `users` via `user_id`
- One-to-many → `inspections` via join through `users`

**Design Decision:** Officers table exists to hold officer-specific metadata without polluting the users table. Identity information (name, email, auth) is not duplicated.

---

## 3. MANUFACTURERS

**Purpose:** Stores manufacturer/packer/importer entities for repeat offender tracking.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `name` | `VARCHAR(500)` | No | — | — |
| `normalized_name` | `VARCHAR(500)` | No | — | **UNIQUE** |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | — |
| `updated_at` | `TIMESTAMPTZ` | No | `NOW()` | — |

**Indexes:**
- `ix_manufacturers_normalized_name` on `normalized_name` (UNIQUE)
- `ix_manufacturers_name` on `name`

**Relationships:**
- One-to-many → `products`
- One-to-many → `inspections`

**Design Decision — Normalization:**
`normalized_name` is a deterministic transformation: lowercase, strip punctuation, collapse whitespace, normalize common abbreviations (e.g., "pvt ltd" → "private limited"). This enables predictable lookups without unsafe fuzzy merging. The original `name` is always preserved. No automatic entity-resolution merging is performed.

---

## 4. PRODUCTS

**Purpose:** Stores product entities linked to manufacturers.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `manufacturer_id` | `UUID` | Yes | — | FK → `manufacturers.id` |
| `product_name` | `VARCHAR(500)` | No | — | — |
| `category` | `VARCHAR(100)` | Yes | — | — |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | — |
| `updated_at` | `TIMESTAMPTZ` | No | `NOW()` | — |

**Indexes:**
- `ix_products_manufacturer_id` on `manufacturer_id`
- `ix_products_category` on `category`

**Relationships:**
- Many-to-one → `manufacturers` via `manufacturer_id`
- One-to-many → `inspections`

---

## 5. INSPECTIONS

**Purpose:** Central entity. Every scan/inspection gets a unique record. Stores AI result metadata, location, compliance outcome, review state, and all 7 model version fields.

### Inspection State Model

Three independent status fields govern the inspection lifecycle:

#### `processing_status`
Tracks the Backend pipeline state.

| Value | Meaning |
|---|---|
| `PENDING` | Inspection created, no AI analysis started |
| `PROCESSING` | AI analysis in progress |
| `COMPLETED` | AI analysis finished (success or partial success) |
| `FAILED` | AI analysis failed fatally |

**Transitions:**
```
PENDING → PROCESSING → COMPLETED
PENDING → PROCESSING → FAILED
FAILED → PROCESSING → COMPLETED  (re-analysis)
```

#### `compliance_status`
The AI Rule Engine's legal determination. Set by AI, stored by Backend. Backend NEVER computes this.

| Value | Meaning |
|---|---|
| `NULL` | No AI result yet (processing_status is PENDING or FAILED) |
| `COMPLIANT` | All applicable rules satisfied |
| `NON_COMPLIANT` | One or more violations detected |
| `INCONCLUSIVE` | Insufficient evidence for determination |

#### `review_status`
Human review workflow state.

| Value | Meaning |
|---|---|
| `NOT_REQUIRED` | AI did not flag for review (`review_required = false`) |
| `PENDING` | AI flagged for review (`review_required = true`), not yet reviewed |
| `REVIEWED` | Officer has reviewed the result |
| `CONFIRMED` | Officer confirmed the AI result |
| `REJECTED` | Officer rejected the AI result |

**Transitions:**
```
NOT_REQUIRED (terminal for non-flagged inspections)
PENDING → REVIEWED → CONFIRMED
PENDING → REVIEWED → REJECTED
```

### Columns

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_code` | `VARCHAR(20)` | No | — | **UNIQUE** |
| `user_id` | `UUID` | Yes | — | FK → `users.id` |
| `officer_id` | `UUID` | Yes | — | FK → `officers.id` |
| `product_id` | `UUID` | Yes | — | FK → `products.id` |
| `manufacturer_id` | `UUID` | Yes | — | FK → `manufacturers.id` |
| **Status Fields** |
| `processing_status` | `VARCHAR(20)` | No | `'PENDING'` | CHECK: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED` |
| `compliance_status` | `VARCHAR(20)` | Yes | `NULL` | CHECK: `COMPLIANT`, `NON_COMPLIANT`, `INCONCLUSIVE` |
| `review_status` | `VARCHAR(20)` | No | `'NOT_REQUIRED'` | CHECK: `NOT_REQUIRED`, `PENDING`, `REVIEWED`, `CONFIRMED`, `REJECTED` |
| `review_required` | `BOOLEAN` | Yes | `NULL` | From AI response |
| `review_reason` | `VARCHAR(50)` | Yes | `NULL` | CHECK: `LOW_IMAGE_QUALITY`, `OCR_UNCERTAIN`, `APPLICABILITY_UNCERTAIN`, `CONFLICTING_INFORMATION`, `PHYSICAL_VERIFICATION_REQUIRED`, `LEGAL_CONTEXT_INSUFFICIENT`, `INSUFFICIENT_EVIDENCE` |
| **Applicability (from AI)** |
| `applicability_status` | `VARCHAR(20)` | Yes | `NULL` | CHECK: `DETERMINED`, `REVIEW_REQUIRED` |
| `applicable_rule_ids` | `JSONB` | Yes | `NULL` | Array of rule ID strings, e.g. `["LM-001", "LM-007"]` |
| **Product Classification (from AI)** |
| `product_name_ai` | `VARCHAR(500)` | Yes | `NULL` | AI-extracted product name |
| `product_category_ai` | `VARCHAR(100)` | Yes | `NULL` | AI classification category |
| `classification_confidence` | `FLOAT` | Yes | `NULL` | 0.0–1.0 |
| **Package Context (from AI)** |
| `package_context` | `VARCHAR(100)` | Yes | `NULL` | retail, wholesale, imported, etc. |
| `context_confidence` | `FLOAT` | Yes | `NULL` | 0.0–1.0 |
| `relevant_metadata` | `JSONB` | Yes | `NULL` | Markers detected by AI |
| **Location (inspection metadata)** |
| `latitude` | `DOUBLE PRECISION` | Yes | `NULL` | GPS latitude |
| `longitude` | `DOUBLE PRECISION` | Yes | `NULL` | GPS longitude |
| `location_text` | `VARCHAR(500)` | Yes | `NULL` | Human-readable address |
| **Model Versions (from AI model_info)** |
| `ocr_version` | `VARCHAR(50)` | Yes | `NULL` | |
| `classification_model_version` | `VARCHAR(50)` | Yes | `NULL` | |
| `embedding_model_version` | `VARCHAR(50)` | Yes | `NULL` | |
| `llm_version` | `VARCHAR(50)` | Yes | `NULL` | |
| `rag_version` | `VARCHAR(50)` | Yes | `NULL` | |
| `rule_engine_version` | `VARCHAR(50)` | Yes | `NULL` | |
| `legal_corpus_version` | `VARCHAR(50)` | Yes | `NULL` | |
| **Officer Notes** |
| `officer_notes` | `TEXT` | Yes | `NULL` | Manual officer observations |
| **Timestamps** |
| `inspection_date` | `TIMESTAMPTZ` | Yes | `NULL` | When physical inspection occurred |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_inspections_inspection_code` on `inspection_code` (UNIQUE)
- `ix_inspections_user_id` on `user_id`
- `ix_inspections_officer_id` on `officer_id`
- `ix_inspections_manufacturer_id` on `manufacturer_id`
- `ix_inspections_product_id` on `product_id`
- `ix_inspections_compliance_status` on `compliance_status`
- `ix_inspections_processing_status` on `processing_status`
- `ix_inspections_inspection_date` on `inspection_date`
- `ix_inspections_created_at` on `created_at`

**Relationships:**
- Many-to-one → `users` via `user_id`
- Many-to-one → `officers` via `officer_id`
- Many-to-one → `products` via `product_id`
- Many-to-one → `manufacturers` via `manufacturer_id`
- One-to-many → `inspection_images`
- One-to-many → `ocr_results`
- One-to-many → `declarations`
- One-to-many → `violations`
- One-to-many → `evidence`
- One-to-many → `legal_references`
- One-to-many → `corrective_actions`
- One-to-many → `reports`
- One-to-many → `audit_logs`

### Location Design Decision

**Decision:** Location fields (`latitude`, `longitude`, `location_text`) are stored **directly on the inspections table**.

**Justification:**
- Each inspection has at most one location.
- There is no use case for location reuse or multi-location inspections.
- A separate locations table would add a join with no query benefit.
- Location does not affect legal compliance — it is metadata only.
- If multi-location support is needed later, a join table can be added without breaking the existing schema.

### Applicability Design Decision

**Decision:** `applicability_status` and `applicable_rule_ids` are stored **directly on the inspections table** rather than in a separate table.

**Justification:**
- There is exactly one applicability result per inspection.
- `applicable_rule_ids` is stored as JSONB because the array of rule ID strings does not require independent relational querying — it is read and displayed as a unit.
- The individual rule IDs are already stored relationally via `legal_references` and `violations.rule_id` for traceability.

---

## 6. INSPECTION_IMAGES

**Purpose:** Stores metadata and storage references for package photographs.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `storage_path` | `VARCHAR(1000)` | No | — | Path/key in storage system |
| `image_type` | `VARCHAR(20)` | No | `'OTHER'` | CHECK: `FRONT`, `BACK`, `SIDE`, `LABEL`, `MRP`, `BARCODE`, `QR`, `EVIDENCE`, `OTHER` |
| `original_filename` | `VARCHAR(500)` | Yes | — | Original upload name (untrusted) |
| `mime_type` | `VARCHAR(100)` | No | — | e.g., `image/jpeg` |
| `file_size` | `INTEGER` | No | — | Bytes |
| `checksum` | `VARCHAR(128)` | Yes | — | SHA-256 hash for evidence integrity |
| `uploaded_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_inspection_images_inspection_id` on `inspection_id`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- One-to-many → `ocr_results` via image_id
- One-to-many → `declarations` via source_image_id
- One-to-many → `evidence` via image_id

**Notes:**
- Multiple images per inspection are supported.
- Original evidence files must never be deleted or overwritten.
- Binary data is NOT stored in PostgreSQL — only metadata and storage path.

---

## 7. OCR_RESULTS

**Purpose:** Stores AI-produced OCR text per image for audit trail.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `image_id` | `UUID` | No | — | FK → `inspection_images.id` |
| `full_text` | `TEXT` | Yes | — | Complete OCR text output |
| `confidence` | `FLOAT` | Yes | — | Overall OCR confidence |
| `ocr_model_version` | `VARCHAR(50)` | Yes | — | OCR model that produced this |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_ocr_results_inspection_id` on `inspection_id`
- `ix_ocr_results_image_id` on `image_id`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- Many-to-one → `inspection_images` via `image_id`

**Notes:**
- OCR results may not always be stored as a separate record if the AI response does not return standalone OCR text. In such cases, OCR information is captured within declarations and evidence.
- If detailed OCR blocks/bounding boxes are needed beyond what declarations store, they may be added as JSONB on this table.

---

## 8. DECLARATIONS

**Purpose:** Stores structured mandatory declaration fields extracted by AI from the package image. Each row is one declaration field.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `field_name` | `VARCHAR(100)` | No | — | e.g., `MRP`, `NET_QUANTITY`, `MANUFACTURER` |
| `raw_value` | `TEXT` | Yes | — | Exact OCR text |
| `normalized_value` | `TEXT` | Yes | — | Standardized format (e.g., `100 g`, `50.00 INR`) |
| `confidence` | `FLOAT` | No | — | Extraction confidence 0.0–1.0 |
| `source_image_id` | `UUID` | Yes | — | FK → `inspection_images.id` |
| `bounding_box` | `JSONB` | Yes | — | `[x, y, w, h]` coordinates |
| `extraction_status` | `VARCHAR(20)` | No | — | CHECK: `FOUND`, `MISSING`, `UNCERTAIN`, `CONFLICTING` |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_declarations_inspection_id` on `inspection_id`
- `ix_declarations_field_name` on `field_name`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- Many-to-one → `inspection_images` via `source_image_id`

**Notes:**
- `extraction_status` is from the canonical AI contract (§5). `MISSING` means the field was expected but not found.
- `bounding_box` is JSONB because it is a fixed-structure coordinate array that does not need relational querying.
- Both `raw_value` and `normalized_value` are preserved — the original AI extraction is never discarded.

---

## 9. VIOLATIONS

**Purpose:** Stores non-compliance violations detected by the AI Rule Engine.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `violation_code` | `VARCHAR(100)` | No | — | e.g., `MISSING_MRP`, `MISSING_QUANTITY` |
| `rule_id` | `VARCHAR(50)` | No | — | Legal rule ID from AI (e.g., `LM-010`) |
| `rule_version` | `VARCHAR(50)` | Yes | — | Version of the rule evaluated |
| `severity` | `VARCHAR(20)` | Yes | — | `HIGH`, `MEDIUM`, `LOW` |
| `description` | `TEXT` | No | — | AI-generated violation explanation |
| `confidence` | `FLOAT` | Yes | — | Detection confidence 0.0–1.0 |
| `evidence_references` | `JSONB` | No | `'[]'` | Array of `evidence_id` strings from AI (e.g., `["EVID_001"]`) |
| `status` | `VARCHAR(20)` | No | `'OPEN'` | CHECK: `OPEN`, `REVIEWED`, `CONFIRMED`, `REJECTED`, `RESOLVED` |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |
| `updated_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_violations_inspection_id` on `inspection_id`
- `ix_violations_violation_code` on `violation_code`
- `ix_violations_rule_id` on `rule_id`
- `ix_violations_status` on `status`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- One-to-many → `evidence` via `violation_id`
- One-to-many → `legal_references` via `violation_id`
- One-to-many → `corrective_actions` via `violation_id`

**Notes:**
- `evidence_references` is JSONB because it stores the AI-provided string array linking to `evidence.evidence_id_ai`. This is kept as JSONB alongside the relational FK (`evidence.violation_id`) because the AI uses string-based references while the database uses UUID FKs.
- `status` tracks the officer review workflow for individual violations (separate from the inspection-level `review_status`).

---

## 10. EVIDENCE

**Purpose:** Stores digital evidence chain items linking violations back to images, OCR, and declarations.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `violation_id` | `UUID` | Yes | — | FK → `violations.id` |
| `evidence_id_ai` | `VARCHAR(100)` | No | — | AI-assigned evidence ID (e.g., `EVID_001`) |
| `image_id` | `UUID` | Yes | — | FK → `inspection_images.id` |
| `evidence_type` | `VARCHAR(50)` | No | — | AI-defined type (e.g., `OCR_BOUNDING_BOX`, `MISSING_FIELD`) |
| `ocr_text` | `TEXT` | Yes | — | Relevant OCR text snippet |
| `bounding_box` | `JSONB` | Yes | — | `[x, y, w, h]` coordinates |
| `declaration_reference` | `VARCHAR(100)` | Yes | — | Links to `declarations.field_name` |
| `rule_id` | `VARCHAR(50)` | Yes | — | Links to the evaluated rule |
| `description` | `TEXT` | Yes | — | Human-readable explanation |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_evidence_inspection_id` on `inspection_id`
- `ix_evidence_violation_id` on `violation_id`
- `ix_evidence_evidence_id_ai` on `evidence_id_ai`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- Many-to-one → `violations` via `violation_id`
- Many-to-one → `inspection_images` via `image_id`

**Notes:**
- `evidence_id_ai` is the AI-assigned string identifier (e.g., `EVID_001`). It is used by `violations.evidence_references` to create the cross-reference. The database also maintains a relational FK via `violation_id`.
- `declaration_reference` is a string linking to a `declarations.field_name` value (e.g., `NET_QUANTITY`). This is a logical reference, not a UUID FK, because the AI uses field names as identifiers.
- Evidence types are AI-defined and stored as-is. Backend does not constrain these to a fixed enum to remain forward-compatible with new AI evidence types.

---

## 11. LEGAL_REFERENCES

**Purpose:** Stores legal provisions retrieved by RAG and evaluated by the Rule Engine. Backend does NOT invent these.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `violation_id` | `UUID` | Yes | — | FK → `violations.id` |
| `rule_id` | `VARCHAR(50)` | No | — | AI rule identifier (e.g., `LM-001`) |
| `rule_number` | `VARCHAR(100)` | Yes | — | Official rule number (e.g., `Rule 6(1)`) |
| `sub_rule` | `VARCHAR(100)` | Yes | — | Specific sub-rule |
| `schedule` | `VARCHAR(100)` | Yes | — | Schedule reference |
| `source_document` | `VARCHAR(255)` | Yes | — | Source PDF/act name |
| `legal_version` | `VARCHAR(50)` | Yes | — | Version of the legal document |
| `rule_version` | `VARCHAR(50)` | Yes | — | AI corpus version of this rule |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_legal_references_inspection_id` on `inspection_id`
- `ix_legal_references_violation_id` on `violation_id`
- `ix_legal_references_rule_id` on `rule_id`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- Many-to-one → `violations` via `violation_id` (nullable — some legal references may apply to the inspection broadly)

**Notes:**
- Legal references may exist at the inspection level (applicable rules) or violation level (specific rule that was violated).
- `violation_id` is nullable to support inspection-level legal references.
- Backend MUST NOT invent `rule_id`, `rule_number`, amendments, or legal requirements.

---

## 12. CORRECTIVE_ACTIONS

**Purpose:** Stores AI/LLM-generated textual corrective suggestions linked to violations.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `violation_id` | `UUID` | Yes | — | FK → `violations.id` |
| `violation_reference` | `VARCHAR(100)` | No | — | AI-provided reference to `violation_code` |
| `action_text` | `TEXT` | No | — | LLM-generated corrective instructions |
| `status` | `VARCHAR(50)` | Yes | — | AI recommendation status (e.g., `GENERATED`) |
| `created_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_corrective_actions_inspection_id` on `inspection_id`
- `ix_corrective_actions_violation_id` on `violation_id`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- Many-to-one → `violations` via `violation_id`

**Notes:**
- `violation_reference` is the AI-provided string linking to `violations.violation_code`. This is stored alongside the relational FK `violation_id` because the AI uses string-based references.
- Backend does NOT invent corrective actions or legal requirements.
- Corrective actions may be empty if LLM fails (see AI contract Example E).

---

## 13. REPORTS

**Purpose:** Stores metadata for generated inspection reports. Reports are generated from persisted Backend data, never from live AI calls.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `inspection_id` | `UUID` | No | — | FK → `inspections.id` |
| `report_path` | `VARCHAR(1000)` | No | — | Storage path for generated report file |
| `report_type` | `VARCHAR(50)` | No | `'INSPECTION'` | e.g., `INSPECTION`, `SUMMARY` |
| `generated_by` | `UUID` | Yes | — | FK → `users.id` |
| `version` | `INTEGER` | No | `1` | Report version (increments on regeneration) |
| `generated_at` | `TIMESTAMPTZ` | No | `NOW()` | |

**Indexes:**
- `ix_reports_inspection_id` on `inspection_id`

**Relationships:**
- Many-to-one → `inspections` via `inspection_id`
- Many-to-one → `users` via `generated_by`

**Notes:**
- Multiple report versions per inspection are supported via the `version` field.
- Report binary files (PDF, etc.) are stored in object/file storage, not in PostgreSQL.
- Reports must be reproducible from stored inspection data. AI is never re-invoked for report generation.

---

## 14. AUDIT_LOGS

**Purpose:** Immutable audit trail for important system events.

| Column | Type | Nullable | Default | Constraints |
|---|---|---|---|---|
| `id` | `UUID` | No | `gen_random_uuid()` | **PRIMARY KEY** |
| `user_id` | `UUID` | Yes | — | FK → `users.id` |
| `inspection_id` | `UUID` | Yes | — | FK → `inspections.id` |
| `action` | `VARCHAR(100)` | No | — | Event type |
| `timestamp` | `TIMESTAMPTZ` | No | `NOW()` | |
| `metadata` | `JSONB` | Yes | — | Additional event context |

**Allowed `action` values:**

| Action | Description |
|---|---|
| `INSPECTION_CREATED` | New inspection record created |
| `IMAGE_UPLOADED` | Package image uploaded |
| `AI_ANALYSIS_STARTED` | AI analysis request sent |
| `AI_ANALYSIS_COMPLETED` | AI analysis finished successfully |
| `AI_ANALYSIS_FAILED` | AI analysis failed |
| `RESULT_REVIEWED` | Officer reviewed AI result |
| `VIOLATION_CONFIRMED` | Officer confirmed a violation |
| `VIOLATION_REJECTED` | Officer rejected a violation |
| `REPORT_GENERATED` | Inspection report generated |
| `MANUAL_NOTE_ADDED` | Officer added observations |
| `INSPECTION_UPDATED` | Inspection metadata updated |

**Indexes:**
- `ix_audit_logs_user_id` on `user_id`
- `ix_audit_logs_inspection_id` on `inspection_id`
- `ix_audit_logs_action` on `action`
- `ix_audit_logs_timestamp` on `timestamp`

**Relationships:**
- Many-to-one → `users` via `user_id`
- Many-to-one → `inspections` via `inspection_id`

**Notes:**
- Audit logs are append-only. They are never updated or deleted.
- `metadata` JSONB stores event-specific context (e.g., AI response time, error details, status change before/after). Secrets must never appear in metadata.

---

## JSONB Usage Summary

| Table | Column | Content | Justification |
|---|---|---|---|
| `inspections` | `applicable_rule_ids` | `["LM-001", "LM-007"]` | Array of strings, read as a unit, individual IDs exist relationally in `legal_references` |
| `inspections` | `relevant_metadata` | `{"export_only": true}` | Opaque AI metadata object, schema varies |
| `declarations` | `bounding_box` | `[x, y, w, h]` | Fixed-structure coordinates |
| `violations` | `evidence_references` | `["EVID_001", "EVID_002"]` | AI string references, relational FK exists via `evidence.violation_id` |
| `evidence` | `bounding_box` | `[x, y, w, h]` | Fixed-structure coordinates |
| `audit_logs` | `metadata` | Event-specific context | Variable structure per event type |

No entity is collapsed into a single opaque JSON blob. All relational traceability is maintained through foreign keys.

---

## Inspection ID Format

**Format:** `INS-YYYY-NNNNNN`

- `YYYY` = 4-digit year
- `NNNNNN` = 6-digit zero-padded sequential number, reset per year

**Example:** `INS-2026-000001`, `INS-2026-000002`

**Implementation:** Generated by the Backend at inspection creation time. The internal primary key remains UUID for performance and distribution safety. `inspection_code` is the human-readable external identifier.
