Absolutely 😎 Here’s a **clean, professional README.md** you can paste directly into the GitHub editor.

````markdown
# ComplianceSahayak

## AI-Assisted Legal Metrology Compliance Platform

ComplianceSahayak is an AI-assisted inspection and compliance platform designed to help analyze packaged commodities against applicable Legal Metrology requirements.

The platform combines computer vision/OCR, AI-assisted field extraction, deterministic compliance evaluation, inspection workflows, analytics, and geospatial inspection tracking into a unified system.

---

## 🚀 Overview

ComplianceSahayak provides two primary interfaces:

### 👤 User Portal

The User Portal allows users to:

- Upload package images for inspection
- Capture multiple package angles
- Run automated OCR and AI-assisted analysis
- Extract packaging declarations
- View compliance results
- Review generated inspection reports
- Access previous scan history

### 🛡️ Officer Portal

The Officer Portal allows compliance officers to:

- Create new package inspections
- Upload multiple package images/angles
- Review extracted package evidence
- Inspect declaration-level OCR results
- Review compliance findings
- Issue inspection notices
- Lock finalized inspection dossiers
- View operational analytics
- View geo-tagged inspections on an interactive map
- Export inspection summaries

---

# ✨ Key Features

## 📸 Multi-Angle Package Inspection

A single inspection can contain multiple package images representing different physical sides or viewing angles.

This allows the system to analyze packaging evidence beyond a single photograph.

---

## 🔍 OCR & AI-Assisted Extraction

The OCR pipeline uses **PaddleOCR** with additional preprocessing and orientation handling for difficult package text.

The system is designed to improve extraction of:

- Small packaging text
- Rotated text
- Edge-region text
- MRP declarations
- Manufacturing / packing dates
- Expiry / best-before information
- Manufacturer information
- Quantity declarations
- Country-of-origin information
- Consumer-care information

OCR results can include:

- Detected text
- Confidence
- Bounding-box coordinates

These results are passed to the AI extraction layer for field-specific interpretation.

---

## 📋 Packaging Declaration Extraction

The platform evaluates common packaging declarations including:

- Manufacturer
- Packer
- Importer
- Product Name
- Net Quantity
- MRP
- Manufacturing / Packing Date
- Expiry / Best Before
- Country of Origin
- Consumer Care

The extraction layer also performs normalization and field-specific candidate selection.

---

## ⚖️ Deterministic Compliance Evaluation

Extracted evidence is evaluated using deterministic compliance rules.

The system is designed to separate:

**OCR evidence → field extraction → rule evaluation → review**

rather than relying only on free-form AI output.

---

## 📁 Inspection Dossiers

Each inspection can be reviewed through a detailed dossier containing:

- Inspection metadata
- Package evidence
- OCR evidence
- Extracted declarations
- OCR confidence
- Rule evaluation
- Compliance status
- Review state
- Officer adjudication actions

---

## 📊 Officer Analytics

The Officer Portal provides operational analytics derived from available inspection data.

Current analytics include:

- Total inspections
- Compliance distribution
- Review-required inspections
- Flagged deficiencies
- Category breakdown
- Date filtering
- Inspection cohort information
- CSV export

---

## 🗺️ Geospatial Inspection Map

Geo-tagged inspections can be displayed on an interactive map.

The Map View supports:

- Inspection markers
- Status filtering
- Inspection information popups
- Dossier navigation
- Audit records associated with mapped inspections
- Focusing the map on a selected inspection

Inspections without valid geographic coordinates are not displayed as map points.

---

## 🔒 Inspection Locking

Officers can lock an inspection dossier after the review process.

A locked inspection is intended to prevent further modification through the normal application workflow.

---

# 🏗️ System Architecture

```text
                         ┌──────────────────────┐
                         │    User / Officer    │
                         │      Web Portal      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   React Frontend     │
                         │ TypeScript + Vite    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         │ Auth / Inspections   │
                         │ Rules / Data APIs    │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────┘       └──────────────┐
                    ▼                                   ▼
          ┌────────────────────┐              ┌────────────────────┐
          │     OCR Service    │              │      AI Service     │
          │     PaddleOCR      │              │ Extraction / AI     │
          │      Port 8001     │              │      Port 8002      │
          └────────────────────┘              └────────────────────┘
                                 │
                                 ▼
                         ┌──────────────────────┐
                         │       Database       │
                         │ Inspections / OCR    │
                         │ Results / Evidence  │
                         └──────────────────────┘
````

---

# 🧰 Technology Stack

## Frontend

* React
* TypeScript
* Vite

## Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL

## AI / Extraction

* Python
* Rule-based field parsers
* AI-assisted extraction
* OCR evidence processing

## OCR

* PaddleOCR
* PP-OCRv6 Medium
* Image preprocessing
* Rotation handling
* OCR confidence and bounding boxes

## Mapping

* Leaflet
* OpenStreetMap

---

# 📂 Repository Structure

```text
ComplianceSahayak/
│
├── SIH_FRONTEND/
│   └── React + TypeScript frontend
│
├── SIH_BACKEND/
│   └── FastAPI backend
│
├── SIH_AI/
│   ├── ai/
│   │   └── AI extraction service
│   │
│   └── ocr_service/
│       └── PaddleOCR service
│
├── .gitignore
└── README.md
```

---

# ⚙️ Local Development

## Prerequisites

Recommended prerequisites:

* Node.js
* npm
* Python 3.11+
* Python 3.14 for the AI environment if required by the current project environment
* PostgreSQL

---

# ▶️ Start the Application

ComplianceSahayak currently runs as four local services.

## 1. Backend — Port 8000

```bash
cd /Users/aayushroy/SIH/SIH_BACKEND/backend

source venv/bin/activate

export PYTHONPATH=$(pwd)

uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/api/v1/health
```

---

## 2. OCR Service — Port 8001

```bash
cd /Users/aayushroy/SIH/SIH_AI/ocr_service

./venv/bin/python3.11 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Health check:

```bash
curl http://localhost:8001/health
```

The OCR service loads its PaddleOCR models during startup if they are not already cached locally.

---

## 3. AI Service — Port 8002

```bash
cd /Users/aayushroy/SIH/SIH_AI

source ai/venv/bin/activate

PYTHONPATH=/Users/aayushroy/SIH/SIH_AI/ai \
uvicorn ai.main:app --host 0.0.0.0 --port 8002
```

Health check:

```bash
curl http://localhost:8002/health
```

---

## 4. Frontend — Port 5173

```bash
cd /Users/aayushroy/SIH/SIH_FRONTEND

npm run dev -- --host 0.0.0.0
```

Open:

```text
http://localhost:5173
```

---

# 🔌 Service Ports

| Service  | Port |
| -------- | ---: |
| Frontend | 5173 |
| Backend  | 8000 |
| OCR      | 8001 |
| AI       | 8002 |

---

# 🔄 Typical Inspection Workflow

```text
Package Image
      │
      ▼
Multi-Angle Evidence Capture
      │
      ▼
OCR Processing
      │
      ▼
OCR Text + Confidence + Bounding Boxes
      │
      ▼
AI-Assisted Field Extraction
      │
      ▼
Normalization / Candidate Selection
      │
      ▼
Deterministic Compliance Rules
      │
      ▼
Inspection Result
      │
      ├───────────────┐
      ▼               ▼
   User Report    Officer Dossier
                      │
              ┌───────┴────────┐
              ▼                ▼
          Adjudication      Analytics
                               │
                               ▼
                              Map
```

---

# 🔎 OCR Pipeline

The current OCR implementation uses PaddleOCR as its primary OCR engine.

The processing flow includes:

```text
Input Image
     │
     ▼
Image Preprocessing
     │
     ▼
PaddleOCR Full-Image Pass
     │
     ▼
Targeted Small / Edge Region Processing
     │
     ▼
Image Upscaling / Enhancement
     │
     ▼
Rotated Region OCR
     │
     ▼
OCR Block Merge + Deduplication
     │
     ▼
Confidence + Bounding Boxes
     │
     ▼
AI Field Extraction
```

The additional processing is intended to improve recognition of difficult real-world packaging text while preserving OCR evidence for downstream verification.

---

# 🧠 Extraction Pipeline

The extraction layer performs field-specific interpretation of OCR evidence.

Examples include:

```text
OCR:
"NO.6KM0039 MFDXJAN.26 EXP.DEC.27"

        ↓

Manufacturing Date:
JAN.26

Expiry Date:
DEC.27
```

Similarly, the extraction pipeline distinguishes between semantic categories such as:

```text
"30 ml"
        ↓
NET QUANTITY

"ML No.: RAJ./COS-2825"
        ↓
Administrative / Licence information
```

rather than treating both as product names.

---

# 🛡️ Security & Configuration

Environment-specific configuration and secrets should remain in local environment files.

Typical files such as:

```text
.env
.env.local
```

should not be committed to GitHub.

The repository's `.gitignore` contains rules intended to prevent common secrets, local environments, and generated files from being tracked.

---

# 🧪 Testing Philosophy

The project uses real package photographs as important OCR/extraction test cases.

Example test categories include:

* Pharmaceutical packaging
* Food packaging
* Cosmetic / personal-care packaging
* Small printed text
* Rotated text
* Dot-matrix or stamped text
* Separate label/value OCR blocks
* Duplicate OCR candidates

The extraction pipeline is designed to prefer **MISSING / REVIEW** over fabricating an unsupported value.

---

# 📌 Project Status

Current platform capabilities include:

* ✅ User Portal
* ✅ Officer Portal
* ✅ Multi-angle inspection uploads
* ✅ PaddleOCR-based OCR pipeline
* ✅ AI-assisted extraction
* ✅ Packaging declaration extraction
* ✅ Deterministic compliance evaluation
* ✅ Inspection dossiers
* ✅ Officer analytics
* ✅ Geo-tagged inspection map
* ✅ Inspection locking
* ✅ Export functionality

The OCR and extraction pipeline remains an active area for experimentation and benchmarking.

---

# 🚀 Future Improvements

Potential future development areas include:

* PaddleOCR-VL benchmarking
* OCR model comparison and ensemble architectures
* Stronger spatial association between labels and values
* Improved product-name classification
* Expanded Legal Metrology rule coverage
* Larger OCR regression datasets
* Backend-driven analytics queries
* Production-scale deployment
* Automated regression testing
* Cloud deployment and observability

---

# 👨‍💻 Author

**Aayush Roy**

GitHub:

[https://github.com/aayushroy1105/ComplianceSahayak](https://github.com/aayushroy1105/ComplianceSahayak)


