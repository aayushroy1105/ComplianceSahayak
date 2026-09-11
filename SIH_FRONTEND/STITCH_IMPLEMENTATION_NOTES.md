# Stitch Implementation Notes

## 1. Design System Integration
The Stitch design system should map directly into `src/index.css` via Tailwind v4 CSS variables. The foundational variables (`--color-primary-*`, `--color-surface-*`, `--radius-*`, `--shadow-*`) are already scaffolded. Stitch's hex codes and token scales should replace or augment these CSS variables rather than introducing a completely separate theme file.

## 2. Reusable Components
The following foundational components created in Phase 1 should be retained and styled using Stitch tokens:
- `AppLayout`: The primary application shell.
- `Sidebar`: The responsive navigation wrapper.
- `TopHeader`: The global context bar.
- `LoadingState`, `EmptyState`, `ErrorState`: Core UI primitives that handle async views.

## 3. Redesign Candidates
The placeholder screens currently residing in `src/pages/user/` and `src/pages/officer/` will need comprehensive redesigns from Stitch:
- **Dashboards**: Must be replaced with rich metric cards, recent activity lists, and actionable alerts.
- **Scan/Inspection Views**: Need complex multi-step forms, image upload zones, and progress indicators.
- **Detail Views**: Need data-dense layouts for evidence, compliance tables, and corrective actions.

## 4. Shared Domain Components
Instead of duplicating logic across User and Officer views, the following components should be built as shared entities in `src/components/domain/`:
- **ComplianceStatus**: A pill/badge component indicating semantic state (Compliant, Non-Compliant, Inconclusive).
- **ViolationCard**: A summary card displaying specific rule breaches.
- **DeclarationTable**: A data grid for expected vs. actual package values.
- **EvidenceViewer**: An image gallery with zoom/pan and OCR bounding box overlays.
- **LegalReference**: An expandable accordion or modal displaying the specific legal text from the LMPC corpus.
- **CorrectiveAction**: A form or checklist for officers to mandate actions.
- **HistoryTable**: A paginated, filterable table for past scans and inspections.

## 5. Semantic Status Styles
All semantic compliance colors (Green for Compliant, Red for Non-Compliant, Amber for Inconclusive) are defined globally in `src/index.css` under `--color-compliance-*`. Components like `ComplianceStatus` should strictly consume these Tailwind classes (e.g., `text-compliance-compliant`, `bg-compliance-non_compliant`) to guarantee visual consistency without hard-coding hex values in the JSX.

## 6. Typography, Spacing, and Tokens
Stitch's typography scales, spacing units, and utility tokens will live inside the `@theme` block of `src/index.css`. Tailwind v4 automatically maps these variables to utility classes.

## 7. Integration Strategy
To integrate Stitch without replacing the architecture:
1. **Tokens First**: Overwrite `src/index.css` variables with Stitch's finalized tokens.
2. **Primitives**: Update `src/components/ui/*` using the new tokens.
3. **Domain Components**: Build the complex shared components in `src/components/domain/` using Stitch's markup.
4. **Composition**: Assemble the domain components inside the existing `src/pages/*` placeholders, connecting them to eventual API data structures defined in `src/types/`.

## 8. Upcoming Design Direction (Phase 2+)
When implementing the finalized Stitch designs, strictly adhere to these UX and data guidelines:
- **Progressive Disclosure**: Do not overwhelm the user. Hide dense information until requested or navigate the user deeper into the workflow.
- **Action-Oriented Officer Dashboard**: The dashboard should be clean and focused on pending tasks, moving the dense history and evidence logs to deeper nested pages.
- **Rich Inspection Results**: The `ScanDetail` and `InspectionDetail` pages must remain information-rich, retaining all required compliance and evidence data.
- **No Fake Data/Claims**: Do not inject invented legal claims or generic "demo/sample" labels into the UI. The application must look like a serious legal-metrology system.
- **Separation of Concerns**: Do not hard-code visual mock data into the core business logic or type definitions. Keep UI presentational.
