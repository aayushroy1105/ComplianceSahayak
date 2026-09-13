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
          │     OCR Service    │              │      AI Service    │
          │     PaddleOCR      │              │ Extraction / AI    │
          │      Port 8001     │              │      Port 8002     │
          └────────────────────┘              └────────────────────┘
                                 │
                                 ▼
                         ┌──────────────────────┐
                         │       Database       │
                         │ Inspections / OCR    │
                         │ Results / Evidence   │
                         └──────────────────────┘
