# SIH 2026 — PS 26034

# LEGAL METROLOGY PACKAGED COMMODITY COMPLIANCE SYSTEM

## Complete Team Blueprint, Architecture, Workflow & Development Rules

---

# 1. PROJECT OBJECTIVE

We are building a web-based AI-assisted inspection and compliance system for checking packaged commodities against the Legal Metrology (Packaged Commodities) Rules, 2011 and applicable amendments.

The system will allow:

1. A USER to scan/upload a packaged commodity and receive a compliance analysis.
2. An OFFICER to perform an inspection, attach evidence, record location/date/time and generate an official-style compliance report.
3. The system to permanently store every inspection/scan in the database for future review.
4. The system to detect repeated violations by the same manufacturer/company.
5. The system to provide legally grounded explanations and corrective suggestions.
6. The system to maintain an evidence trail connecting:

   IMAGE → OCR → EXTRACTED DATA → LEGAL RULE → VIOLATION → REPORT

The system must be designed as a prototype that can later be extended into a production enforcement platform.

---

# 2. CORE IDEOLOGY

The most important principle of the project is:

WE ARE NOT BUILDING:

IMAGE → LLM → "PRODUCT IS ILLEGAL"

We are building:

IMAGE
↓
IMAGE PREPROCESSING
↓
OCR
↓
STRUCTURED DECLARATION EXTRACTION
↓
PRODUCT CLASSIFICATION
↓
PACKAGE/CONTEXT CLASSIFICATION
↓
APPLICABILITY ENGINE
↓
LEGAL KNOWLEDGE RETRIEVAL / RAG
↓
DETERMINISTIC RULE ENGINE
↓
COMPLIANCE DECISION
↓
EVIDENCE MAPPING
↓
LLM EXPLANATION
↓
CORRECTIVE ACTION
↓
STRUCTURED RESULT
↓
BACKEND
↓
DATABASE
↓
USER/OFFICER DASHBOARD

The LLM DOES NOT make the final legal decision.

The deterministic Rule Engine makes the compliance decision.

The LLM only explains the already-determined result and provides textual corrective suggestions based on supplied legal context.

---

# 3. TWO MAIN USERS

Our website has two primary modes.

## A. USER DASHBOARD

A normal user can:

* Upload/scan package images.
* Enter or confirm product information.
* Run a compliance scan.
* View extracted declarations.
* View detected violations.
* View compliance status.
* View legal references.
* View corrective suggestions.
* View evidence associated with violations.
* View previous scans.
* Search scan history.
* Download/view generated reports.
* View scan date/time.
* View location if location was captured.
* View AI analysis details.

The user should have a simplified interface.

---

## B. OFFICER DASHBOARD

The officer dashboard is the enforcement-oriented interface.

Officer capabilities:

* Start a new inspection.
* Capture/upload package photographs.
* Capture multiple package views.
* Capture inspection location.
* Record date/time.
* Run AI analysis.
* Review extracted declarations.
* Review violations.
* Review legal references.
* Review evidence.
* Add manual observations.
* Add supporting photographs/documents.
* Mark AI result as reviewed.
* Generate official-style inspection report.
* View previous inspections.
* Search products/manufacturers.
* View repeat offenders.
* View violation statistics.
* View geographic inspection history.
* Review inspection history by date/location/manufacturer.
* Export reports.

---

# 4. MAIN FEATURES

## REQUIRED / CORE FEATURES

The prototype MUST demonstrate:

1. Image upload/scanning.
2. OCR.
3. Mandatory declaration extraction.
4. Product/package classification.
5. Applicability determination.
6. Legal rule retrieval.
7. Deterministic rule checking.
8. Missing declaration detection.
9. Incorrect/non-standard declaration detection where supported.
10. Quantity/unit checking.
11. MRP checking.
12. Date checking.
13. Manufacturer/packer/importer checking.
14. Consumer care checking.
15. Country of origin checking where applicable.
16. Readability assessment.
17. Compliance/non-compliance/inconclusive status.
18. Violation explanation.
19. Corrective suggestions.
20. Evidence attachment.
21. Report generation.
22. Scan/inspection history.
23. Database storage.
24. Role-based access.
25. Officer dashboard.
26. User dashboard.

---

# 5. OUR INNOVATIVE FEATURES

We have decided to add four major features.

## 5.1 AI-Assisted Corrective Label Suggestion

IMPORTANT:

The AI WILL NOT generate a corrected package image.

It will generate TEXTUAL/THEORETICAL corrective instructions.

Example:

Violation:
MISSING CONSUMER CARE DETAILS

Corrective suggestion:

"Add the prescribed consumer care contact information in the required form and ensure that it is clearly visible and readable on the package."

The LLM must base suggestions only on:

* detected violation
* retrieved legal provision
* structured inspection information

It must not invent legal requirements.

---

# 5.2 Repeat Offender Detection

The system must identify whether the same manufacturer/company has repeatedly committed the same type of violation.

Example popup:

ABC Foods Pvt Ltd

Inspections: 15
Violations: 11
Repeat Violations: 7

Most Frequent:
• Missing Consumer Care
• Incorrect MRP
• Unit Declaration

The backend/database handles historical aggregation.

AI DOES NOT need to perform this calculation.

The database should store every inspection and violation, and the backend should query historical records.

---

# 5.3 Geo-Tagged Inspections

Every officer inspection should optionally contain:

* latitude
* longitude
* date
* time
* inspection location/address if available

The information must be saved with the inspection.

Later, officers can view:

* inspection history
* locations
* date/time
* manufacturer
* violations
* compliance status

Future UI possibility:

MAP → INSPECTION MARKERS → CLICK → INSPECTION DETAILS

The location must be treated as inspection metadata, not as part of the AI decision.

---

# 5.4 Digital Evidence Chain

Every violation must be traceable back to evidence.

Example:

PACKAGE IMAGE
↓
OCR TEXT
↓
BOUNDING BOX
↓
EXTRACTED DECLARATION
↓
LEGAL RULE
↓
RULE ENGINE CHECK
↓
VIOLATION
↓
CORRECTIVE ACTION
↓
REPORT

For example:

Violation:
Missing MRP

Evidence:

* Image ID
* OCR result
* relevant image region
* extracted declarations
* rule ID
* rule version

The officer should be able to understand:

"WHY DID THE SYSTEM FLAG THIS?"

The answer should be visible.

---

# 6. HIGH-LEVEL SYSTEM ARCHITECTURE

The project consists of five major layers.

FRONTEND
↓
BACKEND/API
↓
AI SERVICE
↓
DATABASE / STORAGE
↓
LEGAL KNOWLEDGE BASE

Detailed architecture:

```
                     ┌─────────────────────┐
                     │      USER           │
                     │      DASHBOARD      │
                     └──────────┬──────────┘
                                │
                     ┌──────────▼──────────┐
                     │      OFFICER        │
                     │      DASHBOARD      │
                     └──────────┬──────────┘
                                │
                          HTTPS / REST
                                │
                     ┌──────────▼──────────┐
                     │      BACKEND        │
                     │       API           │
                     │     FastAPI         │
                     └─────┬────────┬──────┘
                           │        │
                     ┌─────▼──┐  ┌──▼──────────┐
                     │   AI   │  │  DATABASE   │
                     │SERVICE │  │ PostgreSQL  │
                     └────┬───┘  └─────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
    ┌────▼────┐      ┌────▼────┐      ┌────▼─────┐
    │   OCR   │      │   RAG   │      │   RULE   │
    │ Paddle  │      │ChromaDB │      │  ENGINE  │
    │   OCR   │      │         │      │          │
    └─────────┘      └────┬────┘      └──────────┘
                          │
                     ┌────▼─────┐
                     │  LEGAL   │
                     │  CORPUS  │
                     └──────────┘
                          │
                     ┌────▼─────┐
                     │   LLM    │
                     │Explanation│
                     └──────────┘
```

# 7. RECOMMENDED TECHNOLOGY STACK

## FRONTEND

Recommended:

* React
* TypeScript
* Vite
* Tailwind CSS
* React Router
* Axios
* Recharts/Chart.js
* Leaflet or another map library if required

Frontend responsibilities:

* UI
* navigation
* image upload
* dashboard
* scan results
* history
* maps
* reports
* authentication UI
* API integration

Frontend must NOT contain legal rules.

---

# 8. BACKEND

Recommended:

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* PostgreSQL
* JWT/session authentication
* Object storage for images/reports

Backend responsibilities:

* Authentication
* Authorization
* User/officer management
* API endpoints
* Database operations
* Inspection creation
* AI service communication
* Scan history
* Repeat offender calculations
* Report generation
* Geo-tag metadata
* Evidence metadata
* File references
* Business logic

Backend must NOT duplicate AI logic.

---

# 9. AI SERVICE

Recommended:

* Python
* FastAPI
* PaddleOCR
* OpenCV
* Pillow
* NumPy
* SentenceTransformers
* ChromaDB
* PyTorch if required by selected models
* LLM API/local model depending on available resources
* Pydantic

AI service responsibilities:

IMAGE
→ OCR
→ extraction
→ classification
→ applicability
→ RAG
→ Rule Engine
→ evidence
→ LLM explanation
→ structured JSON

---

# 10. DATABASE

Recommended:

PostgreSQL.

The database should store persistent application information.

Suggested major tables:

users
officers
products
manufacturers
inspections
inspection_images
ocr_results
declarations
violations
evidence
legal_references
reports
corrective_actions
locations
audit_logs

Potential structure:

## USERS

id
name
email
password_hash/auth_provider
role
created_at

## MANUFACTURERS

id
name
normalized_name
created_at

## PRODUCTS

id
manufacturer_id
product_name
category
created_at

## INSPECTIONS

id
user_id
officer_id
product_id
manufacturer_id
status
inspection_date
created_at
latitude
longitude
location_text
ai_model_version
rule_engine_version
legal_corpus_version
review_status

## INSPECTION_IMAGES

id
inspection_id
storage_path
image_type
uploaded_at

## OCR_RESULTS

id
inspection_id
image_id
text
confidence
ocr_model_version
created_at

## DECLARATIONS

id
inspection_id
field_name
raw_value
normalized_value
confidence
source_image_id
bounding_box

## VIOLATIONS

id
inspection_id
violation_code
severity
description
confidence
rule_id
rule_version
status
created_at

## EVIDENCE

id
inspection_id
violation_id
image_id
evidence_type
ocr_text
bounding_box
description
created_at

## LEGAL_REFERENCES

id
violation_id
rule_id
rule_number
sub_rule
schedule
source_document
legal_version

## CORRECTIVE_ACTIONS

id
violation_id
action_text
created_at

## REPORTS

id
inspection_id
report_path
report_type
generated_at

## AUDIT_LOGS

id
user_id
inspection_id
action
timestamp
metadata

Do NOT unnecessarily duplicate data between tables.

Use foreign keys.

---

# 11. IMPORTANT DATABASE PRINCIPLE

EVERY SCAN MUST HAVE A UNIQUE INSPECTION/SCAN ID.

Example:

INS-2026-000001

Everything associated with that scan must be connected to that ID.

Example:

INS-2026-000001
|
├── Images
├── OCR
├── Declarations
├── Violations
├── Evidence
├── Legal References
├── Corrective Actions
├── Report
└── Location

This makes historical retrieval extremely easy.

---

# 12. AI PIPELINE

The AI pipeline is:

STEP 1 — IMAGE UPLOAD

Receive package image.

Validate:

* file type
* file size
* image dimensions

STEP 2 — PREPROCESSING

Perform where useful:

* resize
* rotation correction
* denoising
* contrast enhancement
* cropping

STEP 3 — OCR

Use PaddleOCR.

Output:

* detected text
* bounding boxes
* confidence

STEP 4 — DECLARATION EXTRACTION

Convert OCR text into structured fields.

Example:

{
"manufacturer": "...",
"packer": "...",
"importer": "...",
"product_name": "...",
"net_quantity": "...",
"mrp": "...",
"manufacturing_date": "...",
"country_of_origin": "...",
"consumer_care": "..."
}

Every extracted field should contain:

* raw value
* normalized value
* confidence
* source
* bounding box where possible

STEP 5 — PRODUCT CLASSIFICATION

Determine product category.

Examples:

* food
* cosmetic
* household
* garment
* electronics
* general commodity

STEP 6 — PACKAGE/CONTEXT CLASSIFICATION

Determine context where possible:

* retail
* wholesale
* imported
* domestic
* export
* industrial
* institutional
* exempt
* special category

Product classification and package classification MUST remain separate.

# 13. APPLICABILITY ENGINE

This is an important component.

Before checking a declaration, determine whether that requirement applies.

Example:

IMAGE
↓
PRODUCT
↓
PACKAGE CONTEXT
↓
APPLICABILITY
↓
APPLICABLE REQUIREMENTS

Output:

{
"status": "DETERMINED",
"applicable_requirements": [
"MRP",
"NET_QUANTITY",
"MANUFACTURER",
"CONSUMER_CARE"
]
}

Possible output:

REVIEW_REQUIRED

when applicability cannot be determined confidently.

# 14. RAG

RAG means Retrieval-Augmented Generation.

Our RAG is NOT the compliance engine.

RAG's job is:

Given:

* product category
* package context
* extracted declaration
* inspection date

retrieve the relevant legal provisions from our verified legal corpus.

Example:

Query:

"Retail packaged food, imported, inspection date X, MRP requirement"

RAG retrieves relevant legal provisions.

Then the Rule Engine evaluates them.

Architecture:

LEGAL DOCUMENTS
↓
CHUNKING
↓
METADATA
↓
EMBEDDINGS
↓
CHROMADB
↓
RETRIEVAL
↓
RELEVANT RULES
↓
RULE ENGINE

# 15. LEGAL CORPUS

IMPORTANT:

NEVER ask an AI coding agent to invent legal rules.

The legal corpus must be created from verified source material.

Each rule should support:

rule_id
rule_number
sub_rule
schedule
text
source_document
amendment
effective_from
effective_until
version
status
category

Example:

{
"rule_id": "LM-RULE-001",
"rule_number": "...",
"sub_rule": "...",
"text": "...",
"source_document": "...",
"amendment": "...",
"effective_from": "...",
"effective_until": "...",
"version": "...",
"status": "ACTIVE"
}

The system must support legal versioning.

Do NOT simply retrieve the latest rule.

The applicable rule can depend on:

inspection date
+
package context
+
product category
+
amendments

# 16. RULE ENGINE

The Rule Engine is deterministic.

It should receive:

* structured declarations
* applicability result
* legal provisions
* normalized values
* package context

Then evaluate compliance.

Output:

COMPLIANT
NON_COMPLIANT
INCONCLUSIVE

Example:

IF applicable MRP requirement
AND MRP is absent
THEN:

violation_code = MISSING_MRP
status = NON_COMPLIANT

The Rule Engine must NOT depend on LLM output.

---

# 17. RULE ENGINE STRUCTURE

Suggested:

app/rules/
engine.py
registry.py
models.py
reason_codes.py
validators/
declarations.py
quantity.py
price.py
dates.py
readability.py
special_cases.py

Reason codes should be standardized.

Examples:

MISSING_MRP
MISSING_MANUFACTURER
MISSING_PACKER
MISSING_IMPORTER
MISSING_NET_QUANTITY
MISSING_CONSUMER_CARE
MISSING_COUNTRY_OF_ORIGIN
MISSING_DATE
INVALID_UNIT
INVALID_QUANTITY
INVALID_MRP
READABILITY_ISSUE
QR_NOT_DETECTED
QR_NOT_READABLE

# 18. QUANTITY AND UNIT ENGINE

Do not treat:

"5 kg"

as a simple string.

Normalize it.

Input:

5 kg

Output:

{
"raw": "5 kg",
"value": 5,
"unit": "kg",
"normalized_value": 5000,
"normalized_unit": "g"
}

Create:

quantity/
parser.py
normalizer.py
unit_validator.py
tolerance.py

The architecture should eventually support Maximum Permissible Error where applicable.

Do not implement unsupported calculations.

# 19. PRICE ENGINE

Keep MRP and Unit Sale Price logically separate.

Suggested:

price/
mrp_parser.py
unit_sale_price.py
price_validator.py

The system should be capable of identifying:

* MRP
* possible MRP formatting issues
* Unit Sale Price where applicable

# 20. QR/BARCODE MODULE

Create:

barcode/
qr_detector.py
qr_decoder.py
barcode_decoder.py

Pipeline:

IMAGE
↓
QR/BARCODE DETECTION
↓
DECODE
↓
EXTRACT DATA
↓
COMPARE/AUGMENT DECLARATIONS
↓
RULE ENGINE

Do not assume QR is applicable to every package.

Applicability must be determined by the legal/context layer.

# 21. READABILITY / FONT SIZE

The system must be conservative.

A normal photograph does NOT automatically provide a reliable physical scale.

Therefore results can be:

VERIFIED
ESTIMATED
INCONCLUSIVE

Do not claim:

"Font size = 1.2 mm"

from pixels alone.

Instead:

"Potential readability/font-size issue detected; physical verification required."

This is safer and more realistic.

# 22. EVIDENCE CHAIN

Every violation must contain evidence.

Example:

{
"violation_type": "MISSING_MRP",

```
"rule_reference": {
    "rule_id": "...",
    "rule_number": "...",
    "version": "..."
},

"evidence": [
    {
        "type": "OCR",
        "source_text": "...",
        "bbox": [...]
    }
]
```

}

Evidence should connect:

IMAGE
→ OCR
→ DECLARATION
→ RULE
→ DECISION

This is one of the major differentiators of our project.

# 23. LLM

Use a pretrained model initially.

DO NOT fine-tune the LLM at the beginning.

Recommended initial approach:

PRETRAINED MODEL
+
RAG
+
PROMPTING
+
DETERMINISTIC RULE ENGINE

Fine-tuning should only be considered later after we have a reliable
human-reviewed dataset.

# 24. LLM RESPONSIBILITIES

The LLM can generate:

1. Human-readable explanation.
2. Textual corrective action.
3. Inspection summary.

The LLM cannot:

* decide legal compliance
* invent rules
* invent rule numbers
* invent evidence
* override Rule Engine
* create unsupported claims
* fabricate legal citations

The LLM receives structured information from the Rule Engine.

# 25. CORRECTIVE ACTION

Input:

Violation:
MISSING_CONSUMER_CARE

Legal context:
[retrieved legal provision]

LLM output:

"The package should include the required consumer care information in the prescribed manner and ensure that the information is clearly visible and readable."

The output must be textual.

NO AI-generated corrected package image.

# 26. CONFIDENCE

Keep separate confidence values:

ocr_confidence
extraction_confidence
classification_confidence
retrieval_score
violation_confidence

Do NOT create a fake:

"Overall legal confidence: 97%"

The final legal decision comes from the Rule Engine.

AI confidence and legal decision must remain separate.

# 27. INCONCLUSIVE STATE

The system must support:

COMPLIANT
NON_COMPLIANT
INCONCLUSIVE

Use INCONCLUSIVE when:

* image is too blurry
* OCR fails
* declaration cannot be reliably extracted
* package type is uncertain
* applicability is uncertain
* evidence is insufficient
* physical measurement cannot be established
* legal context is insufficient

Never force a decision when evidence is insufficient.

# 28. HUMAN REVIEW

AI should be able to return:

review_required: true/false

Set it to true when:

* confidence is insufficient
* image quality is insufficient
* applicability is uncertain
* conflicting information is detected
* physical verification is required

Officer can manually review the case.

# 29. FINAL AI JSON CONTRACT

The AI service should return a stable JSON object similar to:

{
"success": true,

```
"scan_id": "...",

"product": {},

"package_context": {},

"declarations": [],

"applicability": {
    "status": "...",
    "applicable_requirements": []
},

"compliance": {
    "status": "COMPLIANT"
},

"violations": [],

"corrective_actions": [],

"legal_references": [],

"evidence": [],

"review_required": false,

"model_info": {
    "ocr_version": "...",
    "model_version": "...",
    "rag_version": "...",
    "rule_engine_version": "...",
    "legal_corpus_version": "..."
}
```

}

THIS CONTRACT MUST NOT BE CASUALLY CHANGED.

Backend depends on it.

# 30. API CONTRACT

The AI service should expose something like:

POST /ai/analyze

Input:

multipart/form-data

image
scan_id
optional metadata

Output:

structured JSON defined above.

Other AI endpoints may include:

GET /health

POST /ai/ocr

POST /ai/analyze

POST /ai/retrieve-rules

POST /ai/validate

These should only be added if actually required.

The main integration endpoint should remain stable.

# 31. COMPLETE WEBSITE FLOW

## USER FLOW

USER
↓
LOGIN
↓
USER DASHBOARD
↓
UPLOAD PACKAGE IMAGE
↓
OPTIONAL LOCATION
↓
START SCAN
↓
BACKEND CREATES SCAN ID
↓
IMAGE SENT TO AI SERVICE
↓
AI PROCESSING
↓
OCR
↓
EXTRACTION
↓
CLASSIFICATION
↓
APPLICABILITY
↓
RAG
↓
RULE ENGINE
↓
VIOLATIONS
↓
LLM EXPLANATION
↓
AI RETURNS JSON
↓
BACKEND STORES RESULT
↓
REPORT GENERATED
↓
USER SEES RESULT
↓
SCAN SAVED TO HISTORY

# 32. OFFICER FLOW

OFFICER
↓
LOGIN
↓
OFFICER DASHBOARD
↓
NEW INSPECTION
↓
CAPTURE/UPLOAD IMAGES
↓
CAPTURE LOCATION
↓
CAPTURE DATE/TIME
↓
ENTER/CONFIRM BASIC INFORMATION
↓
RUN INSPECTION
↓
BACKEND
↓
AI SERVICE
↓
ANALYSIS
↓
RULE ENGINE
↓
VIOLATIONS
↓
EVIDENCE
↓
REPEAT OFFENDER CHECK
↓
OFFICER REVIEW
↓
OFFICER NOTES
↓
GENERATE REPORT
↓
SAVE EVERYTHING
↓
INSPECTION HISTORY

# 33. REPEAT OFFENDER FLOW

OFFICER INSPECTS:

ABC Foods Pvt Ltd

Backend searches:

previous inspections
+
previous violations

Example:

ABC Foods Pvt Ltd

Inspections: 15
Violations: 11
Repeat Violations: 7

Most frequent:

Missing Consumer Care
Incorrect MRP
Unit Declaration

This should be calculated using database queries.

Do NOT ask the AI/LLM to determine repeat offenders.

# 34. GEO-TAGGED FLOW

Officer starts inspection.

Browser/device provides:

latitude
longitude

Backend stores:

inspection_id
latitude
longitude
timestamp
location_text

Later:

OFFICER DASHBOARD
↓
INSPECTION HISTORY
↓
MAP
↓
CLICK LOCATION
↓
INSPECTION DETAILS

# 35. REPORT GENERATION

Report should include:

Inspection ID
Date/time
Location
Officer
Product
Manufacturer
Images
Extracted declarations
Compliance status
Violations
Legal references
Evidence
Corrective actions
AI/model information
Officer observations
Review status

The report should be generated from backend-stored structured data.

The report should NOT depend on regenerating the AI analysis.

# 36. DIGITAL EVIDENCE CHAIN

Every inspection should maintain:

Inspection ID
↓
Image ID
↓
OCR result
↓
Declaration
↓
Violation
↓
Rule
↓
Evidence
↓
Corrective action
↓
Report

Do not overwrite original evidence.

If an image is replaced or reprocessed, preserve version/history where practical.

# 37. TEAM OF 6 — WORK DIVISION

We have 3 pairs.

PAIR 1 — FRONTEND

Responsibilities:

* React application
* UI
* user dashboard
* officer dashboard
* login UI
* scan UI
* upload UI
* results
* history
* violation display
* report display
* map
* repeat offender popup
* API integration

Does NOT own:

* database schema implementation
* AI pipeline
* legal rules
* OCR
* RAG
* Rule Engine

PAIR 2 — BACKEND + DATABASE

Responsibilities:

* FastAPI/main backend
* authentication
* authorization
* database
* PostgreSQL
* SQLAlchemy
* APIs
* inspection records
* scan history
* report generation
* repeat offender logic
* geo-tag storage
* evidence metadata
* AI service integration

Does NOT own:

* OCR implementation
* RAG
* LLM
* Rule Engine implementation
* frontend UI

PAIR 3 — AI

Responsibilities:

* image preprocessing
* OCR
* declaration extraction
* product classification
* package classification
* applicability engine
* legal corpus
* RAG
* Rule Engine
* quantity/unit processing
* price processing
* QR processing
* LLM
* corrective suggestions
* evidence mapping
* AI API

Does NOT own:

* frontend
* primary application database
* officer dashboard
* user dashboard
* authentication

# 38. FILE OWNERSHIP RULE

This is mandatory.

FRONTEND TEAM can modify:

frontend/
src/components/
src/pages/
src/services/api/
src/hooks/
src/types/

BACKEND TEAM can modify:

backend/
server/
api/
database/
models/
schemas/
services/
reports/

AI TEAM can modify:

ai/
ai-service/
models/
ocr/
rag/
rules/
legal/
pipeline/

Shared files should be minimized.

Nobody should randomly modify another team's files.

# 39. SHARED FILE RULE

The following should be treated as controlled/shared:

README.md
.env.example
docker-compose.yml
API contract
database schema documentation
architecture documentation

If a team needs to modify a shared file:

1. Inform the other team.
2. Make a small change.
3. Commit separately.
4. Explain the change.

Never silently rewrite shared configuration.

# 40. GIT RULES

Use:

main
develop
feature/*

Nobody works directly on main.

Example:

feature/frontend-dashboard
feature/backend-inspection-api
feature/ai-ocr
feature/ai-rag
feature/database-schema

Rules:

* Pull before starting work.
* Commit frequently.
* Use meaningful commit messages.
* Push your branch regularly.
* Create PR before merging.
* Do not force-push shared branches.
* Do not commit .env.
* Do not commit API keys.
* Do not commit huge model files.
* Do not commit generated reports/images unless intentionally required.

# 41. COMMIT NAMING

Use:

feat:
fix:
refactor:
docs:
test:
chore:

Examples:

feat: add inspection creation API

feat: add PaddleOCR pipeline

fix: correct declaration extraction

feat: add repeat offender endpoint

docs: update AI API contract

# 42. ENVIRONMENT VARIABLES

Use .env locally.

Commit:

.env.example

Never commit:

.env

Examples:

DATABASE_URL=
JWT_SECRET=
AI_SERVICE_URL=
LLM_API_KEY=
STORAGE_URL=
CHROMA_PATH=

Never hard-code keys.

# 43. INTER-TEAM CONTRACT

The most important rule:

TEAMS SHOULD INTEGRATE THROUGH CONTRACTS, NOT THROUGH RANDOM DIRECT FILE EDITS.

Frontend talks to Backend through REST API.

Backend talks to AI through AI API.

Backend talks to Database.

AI talks to Legal Corpus/Vector DB internally.

Architecture:

FRONTEND
↓ REST
BACKEND
↓ REST
AI SERVICE
↓
OCR/RAG/RULE ENGINE/LLM

# 44. DO NOT CONNECT FRONTEND DIRECTLY TO AI

Frontend should NOT call:

PaddleOCR
ChromaDB
LLM
Rule Engine

Frontend only talks to Backend.

Backend calls AI service.

This keeps the architecture clean and secure.

# 45. DO NOT CONNECT FRONTEND DIRECTLY TO DATABASE

Frontend must never directly manipulate PostgreSQL.

Frontend:

→ Backend API

Backend:

→ PostgreSQL

# 46. AI SERVICE SHOULD NOT OWN THE MAIN APPLICATION DATABASE

AI can have its own internal components such as:

ChromaDB
model cache
temporary processing data

But the main inspection history belongs to the Backend/PostgreSQL.

The AI returns structured results.

Backend persists them.

# 47. API INTEGRATION ORDER

Do NOT wait until the end to integrate.

Integration should happen in this order:

1. Backend creates /health.
2. AI creates /health.
3. Backend calls AI /health.
4. Backend creates /ai/analyze integration.
5. AI returns MOCK JSON.
6. Backend stores MOCK JSON.
7. Frontend displays MOCK JSON.
8. Replace AI mock with OCR.
9. Replace OCR mock with real pipeline.
10. Add RAG.
11. Add Rule Engine.
12. Add LLM.
13. Add final report.

This ensures the teams can work independently.

# 48. MOCK MODE

AI must support mock mode.

Example:

MOCK_AI=true

Mock response:

{
"success": true,
"compliance": {
"status": "NON_COMPLIANT"
},
"violations": [
{
"violation_code": "MISSING_MRP"
}
]
}

This allows:

Frontend → Backend → AI

integration before the real AI is finished.

# 49. DEBUG MODE

AI should support:

DEBUG_PIPELINE=true

Then developers can inspect:

original image
preprocessed image
OCR
bounding boxes
extracted fields
classification
applicability
retrieved rules
Rule Engine
LLM output

Do not expose debug internals in production.

# 50. LATENCY MONITORING

Record:

preprocessing_time
ocr_time
extraction_time
classification_time
rag_time
rule_engine_time
llm_time
total_time

Example:

OCR: 1.42 sec
Extraction: 0.21 sec
RAG: 0.18 sec
Rule Engine: 0.02 sec
LLM: 1.91 sec
TOTAL: 3.74 sec

This helps optimize the pipeline.

# 51. AI MODEL STRATEGY

Initial approach:

PRETRAINED OCR MODEL
+
PRETRAINED EMBEDDING MODEL
+
RAG
+
DETERMINISTIC RULE ENGINE
+
PRETRAINED LLM

Do NOT immediately fine-tune.

Fine-tuning is optional future work.

The biggest accuracy improvement initially will come from:

* better OCR
* better extraction
* better legal corpus
* better retrieval
* better rule definitions
* better evidence handling

# 52. WHY RAG EXISTS

RAG is used because the legal knowledge is large and can change.

Instead of putting all legal rules into the LLM prompt every time:

User image
↓
extract context
↓
retrieve relevant legal provisions
↓
send only relevant provisions
↓
LLM/rule system

RAG improves:

* relevance
* legal grounding
* context size
* maintainability

But:

RAG ≠ Rule Engine.

RAG finds the relevant law.

Rule Engine evaluates compliance.

# 53. PROTOTYPE RULE SCOPE

DO NOT attempt to implement every Legal Metrology provision for the college prototype.

Start with a strong subset.

Recommended initial checks:

1. MRP
2. Manufacturer/packer/importer
3. Net quantity
4. Unit declaration
5. Date declaration
6. Consumer care
7. Country of origin where applicable
8. Unit Sale Price where applicable
9. Basic readability
10. QR/electronic information where applicable

Architecture must support additional rules later.

# 54. TEST CASES

Minimum AI test dataset:

1. Fully compliant package.
2. Missing MRP.
3. Missing manufacturer.
4. Missing net quantity.
5. Missing consumer care.
6. Incorrect unit.
7. Missing date.
8. Imported product.
9. Multiple violations.
10. Blurry image.
11. Rotated image.
12. Poor lighting.
13. Small text.
14. QR package.
15. Inconclusive package.

Every stage should have tests.

# 55. ERROR HANDLING

Never let the entire application crash because OCR fails.

Possible AI errors:

OCR_FAILURE
INVALID_IMAGE
LOW_IMAGE_QUALITY
EXTRACTION_FAILURE
CLASSIFICATION_FAILURE
RAG_FAILURE
RULE_ENGINE_ERROR
LLM_FAILURE

If LLM fails:

The Rule Engine result should still be returned.

Example:

Compliance:
NON_COMPLIANT

Explanation:
TEMPORARILY_UNAVAILABLE

The LLM must never be a single point of failure for compliance.

# 56. SECURITY

Never:

* expose API keys
* expose database credentials
* allow frontend direct DB access
* trust user-provided role values
* allow arbitrary file execution
* accept unlimited image sizes
* expose internal AI endpoints publicly without protection

Validate uploads.

Use authentication and authorization.

Officer endpoints should require officer role.

# 57. DATA OWNERSHIP

Backend/PostgreSQL:

SOURCE OF TRUTH FOR INSPECTION DATA.

AI:

SOURCE OF TRUTH FOR CURRENT AI PROCESSING RESULT ONLY.

Frontend:

DISPLAY LAYER.

Legal Corpus:

SOURCE OF TRUTH FOR VERIFIED LEGAL KNOWLEDGE.

Rule Engine:

SOURCE OF TRUTH FOR DETERMINISTIC COMPLIANCE DECISION.

# 58. VERSION EVERYTHING IMPORTANT

Store:

OCR model version
classification model version
embedding model version
LLM version
RAG version
Rule Engine version
Legal Corpus version

Why?

If an inspection is reviewed months later, we should know:

"Which models and legal rules produced this result?"

# 59. DEVELOPMENT ORDER FOR THE ENTIRE TEAM

PHASE 1 — CONTRACTS

All teams agree on:

* folder structure
* API contract
* database schema
* AI JSON schema
* environment variables

PHASE 2 — SKELETON

Frontend:
basic dashboard

Backend:
FastAPI + PostgreSQL

AI:
FastAPI + /health + mock /analyze

PHASE 3 — INTEGRATION

Frontend
↓
Backend
↓
AI MOCK
↓
Database

PHASE 4 — REAL AI

OCR
↓
Extraction
↓
Classification

PHASE 5 — LEGAL INTELLIGENCE

Applicability
↓
RAG
↓
Rule Engine

PHASE 6 — ENHANCEMENTS

QR
Quantity
Price
Evidence
LLM

PHASE 7 — OFFICER FEATURES

Geo-tagging
History
Repeat offenders
Reports

PHASE 8 — FINAL INTEGRATION

Full end-to-end testing.

# 60. TEAM DAILY WORKFLOW

At the beginning of each work session:

1. Pull latest develop.
2. Check whether another team changed shared contracts.
3. Work only on your team's branch.
4. Test locally.
5. Commit.
6. Push.
7. Inform the team of API/schema changes.

At the end:

* Push code.
* Mention completed work.
* Mention blockers.
* Mention changed API/schema.
* Mention what other teams need to know.

# 61. WHAT COUNTS AS A BLOCKER

Immediately tell the team if:

* API response changes.
* Database schema changes.
* AI JSON changes.
* Authentication changes.
* Environment variable changes.
* File ownership conflict occurs.
* A dependency breaks another team's environment.

Do not silently "fix" another team's module.

# 62. DEMO SCENARIO

For the college/SIH demonstration, use one carefully prepared product.

Example:

OFFICER
↓
New Inspection
↓
Capture package image
↓
GPS captured
↓
AI Scan
↓
OCR extracts:

Manufacturer
MRP
Net Quantity
Date
Consumer Care
Country of Origin

↓
Applicability Engine
↓
RAG retrieves applicable provision
↓
Rule Engine detects:

MISSING_CONSUMER_CARE
INVALID_UNIT

↓
Evidence shown on image
↓
Legal references displayed
↓
AI explains violations
↓
Corrective suggestions displayed
↓
Backend stores inspection
↓
Repeat offender check
↓
Report generated
↓
Inspection appears in history/map

This single flow demonstrates almost the entire architecture.

# 63. WHAT MAKES OUR PROJECT DIFFERENT

Our differentiators should be:

1. AI-assisted package inspection.
2. Deterministic legal Rule Engine.
3. RAG-based legal grounding.
4. Versioned legal knowledge.
5. Evidence traceability.
6. Corrective action suggestions.
7. Repeat offender detection.
8. Geo-tagged inspections.
9. Historical inspection repository.
10. Officer dashboard.
11. Human-review support.
12. Explainable AI.

The strongest message:

"AI assists the officer; it does not replace the legal decision-making process."

# 64. MOST IMPORTANT ARCHITECTURAL RULES

RULE 1:
Frontend never talks directly to Database.

RULE 2:
Frontend never talks directly to AI.

RULE 3:
Backend is the central application API.

RULE 4:
AI service is independently deployable.

RULE 5:
Rule Engine makes compliance decisions.

RULE 6:
LLM never overrides Rule Engine.

RULE 7:
RAG retrieves legal context; it does not determine compliance.

RULE 8:
Legal rules must come from verified sources.

RULE 9:
Every inspection gets a unique ID.

RULE 10:
Every violation must have evidence.

RULE 11:
Every important model/rule system is versioned.

RULE 12:
Insufficient evidence → INCONCLUSIVE.

RULE 13:
Do not hard-code secrets.

RULE 14:
Do not modify another team's files without agreement.

RULE 15:
Do not change API/database contracts casually.

RULE 16:
Mock integration must work before real AI integration.

RULE 17:
Do not try to implement the entire legal framework for the first prototype.

RULE 18:
Do not fine-tune the LLM before we have a verified dataset.

RULE 19:
Do not fabricate legal rules.

RULE 20:
Build modularly so every major AI component can be replaced.

# 65. FINAL SYSTEM FLOW

The complete system should ultimately behave like this:

```
                USER / OFFICER
                      |
                      v
                WEB INTERFACE
                      |
                      v
                BACKEND API
                      |
           ┌──────────┴──────────┐
           |                     |
           v                     v
      APPLICATION DB        AI SERVICE
           |                     |
           |              IMAGE PREPROCESSING
           |                     |
           |                     v
           |                    OCR
           |                     |
           |                     v
           |              DECLARATION EXTRACTION
           |                     |
           |                     v
           |              PRODUCT CLASSIFICATION
           |                     |
           |                     v
           |              PACKAGE CLASSIFICATION
           |                     |
           |                     v
           |             APPLICABILITY ENGINE
           |                     |
           |                     v
           |                    RAG
           |                     |
           |              LEGAL PROVISIONS
           |                     |
           |                     v
           |               RULE ENGINE
           |                     |
           |          ┌──────────┴─────────┐
           |          |                    |
           |          v                    v
           |      VIOLATIONS            EVIDENCE
           |          |                    |
           |          └──────────┬─────────┘
           |                     |
           |                     v
           |                    LLM
           |                     |
           |          ┌──────────┴─────────┐
           |          |                    |
           |          v                    v
           |      EXPLANATION       CORRECTIVE ACTION
           |          |                    |
           |          └──────────┬─────────┘
           |                     |
           |                     v
           |              STRUCTURED JSON
           |                     |
           └──────────────┬──────┘
                          |
                          v
                   BACKEND STORES
                          |
           ┌──────────────┼──────────────┐
           |              |              |
           v              v              v
       HISTORY        REPORTS        ANALYTICS
           |              |              |
           v              v              v
        USER UI      OFFICER UI     REPEAT OFFENDER
                                      + GEO MAP
```

# 66. END GOAL

The final prototype should demonstrate that a package can be:

SCANNED
↓
UNDERSTOOD
↓
CHECKED AGAINST VERIFIED LEGAL KNOWLEDGE
↓
DETERMINISTICALLY VALIDATED
↓
EXPLAINED
↓
SUPPORTED WITH EVIDENCE
↓
CORRECTED THROUGH TEXTUAL GUIDANCE
↓
GEO-TAGGED
↓
STORED
↓
REVIEWED LATER
↓
CONNECTED TO MANUFACTURER HISTORY
↓
USED FOR ENFORCEMENT ANALYTICS

The project should feel like an actual digital inspection platform,
not merely an OCR + chatbot application.

==============================================================
GOLDEN RULE
===========

AI ASSISTS.
RAG RETRIEVES.
RULE ENGINE DECIDES.
BACKEND STORES.
FRONTEND PRESENTS.
OFFICER REVIEWS.

==============================================================