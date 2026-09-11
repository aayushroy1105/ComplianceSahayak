---
name: Statutory Metrology Inspection System
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fd'
  on-secondary-container: '#57657b'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#111c2d'
  on-tertiary-container: '#79849a'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d5e3fd'
  secondary-fixed-dim: '#b9c7e0'
  on-secondary-fixed: '#0d1c2f'
  on-secondary-fixed-variant: '#3a485c'
  tertiary-fixed: '#d8e3fb'
  tertiary-fixed-dim: '#bcc7de'
  on-tertiary-fixed: '#111c2d'
  on-tertiary-fixed-variant: '#3c475a'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-xl:
    fontFamily: Public Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl-mobile:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-lg:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Public Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-legal:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  evidence-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: -0.02em
  evidence-mono-bold:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
  badge-label:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 14px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  space-xxs: 0.125rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-base: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  table-cell-py: 0.5rem
  table-cell-px: 0.75rem
  panel-padding: 1.25rem
  gutter-desktop: 1.5rem
  gutter-tablet: 1rem
  gutter-mobile: 0.75rem
---

## Brand & Style

The design system establishes a high-trust, rigorous statutory inspection environment tailored for enforcement officers, verification laboratories, and compliance adjudicators. It prioritizes unimpeachable authority, legal auditability, and cognitive precision. Visual elements reflect strict adherence to the Legal Metrology (Packaged Commodities) Rules, stripping away decorative trends in favor of an institutional, high-utility operational console.

### Visual Language & Aesthetic Direction
- **Style Archetype:** Institutional Modernism / Precision Instrument UI. The interface relies on crisp 1px structural framing, structured key-value data grids, high-density tables, and uncompromising typographic hierarchy.
- **Atmosphere:** Evokes judicial objectivity, precision engineering, and statutory finality. Every element looks anchored, verified, and legally binding.
- **Information Density:** High to dense. Officers and compliance reviewers need full visibility over statutory declarations (MRP, net quantity, manufacturer address, country of origin, date of manufacture) alongside evidentiary optical character verification records without superfluous padding.

## Colors

The color palette is calibrated for long audit sessions, high contrast readability, and immediate risk recognition. Surfaces remain crisp and neutral, preserving color accents strictly for semantic legal validation status.

### Role Assignments
- **Primary (`#0F172A` - Deep Slate):** Primary headers, statutory command bars, top-level navigation, and prominent structural anchor points.
- **Secondary (`#334155` - Slate Charcoal):** Secondary navigation tabs, table section headers, column groupings, and primary body text.
- **Tertiary (`#1E293B` - Institutional Navy Slate):** High-level card headers, modal titles, and active selection states on utility toolbars.
- **Neutral Surface (`#F8FAFC` - Off-White Slate Base):** Canvas background, panel backdrops, and secondary row zebra striping. Surface containers use pure white (`#FFFFFF`) to ensure maximum legibility against borders.
- **Border Crisp Line (`#E2E8F0`):** Standard 1px structural rule for cards, data grids, key-value delimiters, and input outlines.

### Semantic Tokens
- **COMPLIANT:**
  - Base: `#059669` (Emerald 600)
  - Surface: `#ECFDF5` (Emerald 50)
  - Border: `#A7F3D0` (Emerald 200)
  - Text: `#065F46` (Emerald 800)
- **NON_COMPLIANT:**
  - Base: `#DC2626` (Crimson 600)
  - Surface: `#FEF2F2` (Rose 50)
  - Border: `#FECACA` (Rose 200)
  - Text: `#991B1B` (Rose 800)
- **INCONCLUSIVE / MANUAL_REVIEW:**
  - Base: `#D97706` (Amber 600)
  - Surface: `#FFFBEB` (Amber 50)
  - Border: `#FDE68A` (Amber 200)
  - Text: `#92400E` (Amber 800)
- **TRACEABILITY / METROLOGY REFERENCE:**
  - Base: `#2563EB` (Blue 600)
  - Surface: `#EFF6FF` (Blue 50)
  - Border: `#BFDBFE` (Blue 200)
  - Text: `#1E40AF` (Blue 800)

## Typography

The type system blends the administrative, institutional clarity of **Public Sans** for structure and headings, the neutral precision of **Inter** for forms, key-value pairs, and body content, and **JetBrains Mono** for forensic and legal traceability tokens (e.g., Batch IDs, Hash Signatures, OCR confidence scores, Net Quantity values, GPS coordinate strings).

### Application Rules
- **Rule Titles and Statutory References:** Always rendered in `headline-sm` or `body-md` bold, utilizing sentence case with standardized statutory numbering (e.g., *Rule 6(1)(a) - Declared Name of Commodity*).
- **Key-Value Formats:** Field labels use `label-legal` in uppercase slate (`#64748B`), and field values use `body-md` in `#0F172A` with strict vertical baseline alignment.
- **Metrological & Evidence Traceability:** Physical inspection measurements, scanned bar-codes, GTINs, digital cryptographic proofs, and measurement tolerance calculations require `evidence-mono`.
- **Optical Character Verification Displays:** When presenting raw detected packaging text side-by-side with statutory fields, use `evidence-mono` paired with a confidence badge.

## Layout & Spacing

The layout model is anchored on a rigid 4px/8px structural grid designed for data-intensive split views: statutory rule inspection lists on the left, packaging artifact evidence (high-resolution photo inspection / OCR bounding boxes) on the right.

### Grid Architecture
- **Desktop (1280px and above):** 12-column layout or fixed two-pane audit split (60% Evidence Inspection Canvas, 40% Statutory Checklist Panel). Gutter is fixed at 24px (`gutter-desktop`), outer margin at 32px.
- **Tablet (768px – 1279px):** 8-column layout. Gutter shrinks to 16px (`gutter-tablet`), with statutory panels collapsing into collapsible tabbed sections below the evidence viewport.
- **Mobile / Field Device (320px – 767px):** 4-column layout with 12px outer safe margins (`gutter-mobile`). Data tables reflow into dense structured key-value audit summary cards.

### Dense Packing Philosophy
To prevent vertical scroll fatigue during high-volume sample processing, table row heights are locked at 36px (compact) to 44px (default). Internal data margins avoid decorative breathing room: cards employ a strict `panel-padding` of 20px (1.25rem) with continuous 1px separation boundaries.

## Elevation & Depth

Visual hierarchy does not rely on deep drop shadows, which introduce ambiguity in administrative interfaces. Depth is achieved strictly via **tonal layering**, **1px crisp borders**, and **low-radius ambient focus rings**.

### Elevation Tiers
- **Tier 0 (Base Canvas):** `#F8FAFC`. The foundational backdrop for all page containers.
- **Tier 1 (Surface Containers & Grids):** `#FFFFFF` with a continuous `1px solid #E2E8F0` border. No drop shadow. All audit forms, checklists, and statutory record tables operate on this tier.
- **Tier 2 (Popovers, Sticky Table Headers, Command Ribbons):** `#FFFFFF` with a `1px solid #CBD5E1` border and a micro ambient shadow: `0 1px 3px 0 rgba(15, 23, 42, 0.08), 0 1px 2px -1px rgba(15, 23, 42, 0.04)`.
- **Tier 3 (Modals, Seizure Notices, Adjudication Overlays):** `#FFFFFF` with a `1px solid #94A3B8` border and a structural shadow: `0 10px 15px -3px rgba(15, 23, 42, 0.12), 0 4px 6px -4px rgba(15, 23, 42, 0.08)`. Modals use a statutory dark backdrop overlay: `rgba(15, 23, 42, 0.6)`.

### Layer Framing
Inset borders (`box-shadow: inset 0 0 0 1px #E2E8F0`) are preferred over floating shadows to ensure borders remain sharp on high-DPI displays and retain crisp division when printed or exported directly to official court-ready PDF notices.

## Shapes

The design system enforces a disciplined `Soft` geometric structure (`roundedness: 1`). Soft 4px radii avoid the clinical harshness of completely sharp corners while preventing the casual or consumer appearance associated with rounded pills.

### Corner Radius Mapping
- **Action Buttons, Badges, Field Inputs, Table Checkboxes:** `rounded` (4px / 0.25rem).
- **Inspection Cards, Data Panels, Evidence Viewer Framing:** `rounded-md` (6px / 0.375rem).
- **System Modals, Inspection Flyouts:** `rounded-lg` (8px / 0.5rem).
- **Status Tags / Verification Badges:** Strictly 2px to 4px. Fully rounded pill shapes (`rounded-full`) are strictly forbidden, as statutory records demand structured, stamp-like indicators.

## Components

### 1. Verification & Compliance Badges
- **COMPLIANT:** Background `#ECFDF5`, border `1px solid #A7F3D0`, text `#065F46`. Prepended with an emerald geometric checkmark (`✓`).
- **NON_COMPLIANT:** Background `#FEF2F2`, border `1px solid #FECACA`, text `#991B1B`. Prepended with an alert cross (`✕`) or octagonal warning sign.
- **MANUAL_REVIEW / INCONCLUSIVE:** Background `#FFFBEB`, border `1px solid #FDE68A`, text `#92400E`. Prepended with a triage circle (`!`).
- **Layout:** Micro height (22px), uppercase `badge-label`, padding `2px 8px`, border radius `3px`.

### 2. Statutory Inspection Key-Value Lists
- Constructed inside 1px bordered containers. Each row features a 2-column split:
  - Left column (35%): Label in `label-legal` slate `#64748B`, background `#F8FAFC`, border-right `1px solid #E2E8F0`.
  - Right column (65%): Value in `body-md` slate `#0F172A`, background `#FFFFFF`. If values are metric measurements (e.g., `500 g ± 1.5%`), the value uses `evidence-mono`.

### 3. Dense Compliance Tables
- Headers: Background `#F1F5F9`, text `#334155`, font `label-legal`, letter spacing `0.05em`, border bottom `2px solid #CBD5E1`. Height `36px`.
- Rows: Default `#FFFFFF`, hover `#F8FAFC`, selected `#F1F5F9`. Border bottom `1px solid #E2E8F0`. Cell padding `8px 12px`.
- Zebra striping: Alternate rows use `#FAFAFA` only for audit lists exceeding 20 rows.

### 4. Form Inputs & Inspection Controls
- Base input: Height `36px`, background `#FFFFFF`, border `1px solid #CBD5E1`, text `body-md` `#0F172A`, border radius `4px`.
- Focus state: Border `1px solid #0F172A`, outline `2px solid rgba(15, 23, 42, 0.15)`, outline offset `1px`.
- Error state: Border `1px solid #DC2626`, background `#FEF2F2` (tinted 20%), text `#991B1B`.

### 5. Buttons
- **Primary (Enforce / Issue Notice / Validate):** Background `#0F172A`, text `#FFFFFF`, hover `#1E293B`, active `#020617`. Height `36px`, font `body-md` bold, padding `0 16px`, border radius `4px`.
- **Secondary (Inspect / Export Record):** Background `#FFFFFF`, border `1px solid #CBD5E1`, text `#334155`, hover `#F8FAFC`.
- **Destructive (Reject Declaration / Issue Seizure Order):** Background `#DC2626`, text `#FFFFFF`, hover `#B91C1C`.

### 6. Evidence Traceability Card
- Header: `#1E293B` text `#F8FAFC`, displaying verified Rule citation, timestamp (UTC/IST), and Officer Hash ID in `evidence-mono`.
- Body: Framing high-resolution package scans with color-coded bounding boxes mapped directly to statutory fields (Green = Declared MRP confirmed, Red = Missing Packer Address, Amber = Illegible Font Height of Net Quantity declaration).
