from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
import io
import uuid
from datetime import datetime
from typing import Optional
from app.models.report import Report
from app.models.user import User
from app.services.inspection_service import get_inspection
from app.services.storage_service import storage_service

async def generate_markdown_report(inspection) -> bytes:
    md = []
    md.append(f"# Inspection Report: {inspection.inspection_code}")
    md.append(f"**Generated At:** {datetime.utcnow().isoformat()}Z")
    md.append("---")
    
    # 1-7: Metadata
    md.append("## 1. Inspection Metadata")
    md.append(f"- **Inspection ID:** {inspection.id}")
    md.append(f"- **Date:** {inspection.inspection_date}")
    loc_text = inspection.location_text or 'N/A'
    md.append(f"- **Location:** {loc_text} (Lat: {inspection.latitude}, Lng: {inspection.longitude})")
    md.append(f"- **Officer Notes:** {inspection.officer_notes or 'None'}")
    
    prod = getattr(inspection, 'product', None)
    prod_name = getattr(prod, 'product_name', getattr(prod, 'name', None)) or inspection.product_name_ai or 'Unknown'
    manuf_name = inspection.manufacturer.name if getattr(inspection, 'manufacturer', None) else 'Unknown Manufacturer'
    md.append(f"- **Product:** {prod_name}")
    md.append(f"- **Manufacturer:** {manuf_name}")
    
    # Model Versions
    md.append("\n## 2. Model Versions")
    md.append(f"- OCR Version: {inspection.ocr_version or 'N/A'}")
    md.append(f"- Rule Engine Version: {inspection.rule_engine_version or 'N/A'}")
    
    # Compliance & Review Status
    md.append("\n## 3. Compliance Status")
    md.append(f"- **Compliance:** {inspection.compliance_status or 'PENDING'}")
    md.append(f"- **Review Required:** {inspection.review_required}")
    md.append(f"- **Review Reason:** {inspection.review_reason or 'N/A'}")
    
    # Extracted Declarations
    md.append("\n## 4. Extracted Declarations")
    if inspection.declarations:
        for d in inspection.declarations:
            md.append(f"- **{d.field_name}**: {d.raw_value} (Confidence: {d.confidence})")
    else:
        md.append("*No declarations extracted.*")
        
    # Violations & Corrective Actions
    md.append("\n## 5. Violations & Corrective Actions")
    if inspection.violations:
        for v in inspection.violations:
            md.append(f"### Violation: {v.violation_code}")
            md.append(f"- **Rule ID:** {v.rule_id} (Version: {v.rule_version})")
            md.append(f"- **Severity:** {v.severity}")
            md.append(f"- **Description:** {v.description}")
            md.append(f"- **Status:** {v.status}")
            md.append(f"- **Evidence Refs:** {', '.join(v.evidence_references)}")
            
            if v.corrective_actions:
                md.append("**Corrective Actions:**")
                for ca in v.corrective_actions:
                    md.append(f"  - {ca.action_text} (Status: {ca.status})")
            else:
                md.append("**Corrective Actions:** None")
    else:
        md.append("*No violations found.*")
        
    # Evidence
    md.append("\n## 6. Evidence")
    if getattr(inspection, 'evidence', None):
        for e in inspection.evidence:
            md.append(f"- **ID:** {e.evidence_id_ai} | **Type:** {e.evidence_type} | **Rule:** {e.rule_id}")
            if e.ocr_text:
                md.append(f"  - OCR Text: {e.ocr_text}")
    else:
        md.append("*No evidence logged.*")
        
    # Images
    md.append("\n## 7. Inspection Images")
    if inspection.images:
        for img in inspection.images:
            md.append(f"- {img.image_type} Image: `{img.original_filename}` ({img.storage_path})")
    else:
        md.append("*No images uploaded.*")
        
    return "\n".join(md).encode('utf-8')

async def generate_report_for_inspection(db: AsyncSession, current_user: User, inspection_id: str) -> Report:
    # 1. Get inspection (This handles authorization)
    inspection = await get_inspection(db, current_user, inspection_id)
    
    # 2. Check if previous report exists to increment version
    query = select(Report).where(Report.inspection_id == inspection.id).order_by(Report.version.desc())
    result = await db.execute(query)
    last_report = result.scalars().first()
    new_version = (last_report.version + 1) if last_report else 1
    
    # 3. Generate Markdown content
    md_bytes = await generate_markdown_report(inspection)
    
    # 4. Save file via StorageService
    filename = f"report_{inspection.inspection_code}_v{new_version}.md"
    storage_path = await storage_service.save_file(md_bytes, filename)
    
    # 5. Create DB Record
    report = Report(
        inspection_id=inspection.id,
        report_path=storage_path,
        report_type="MARKDOWN",
        version=new_version,
        generated_by=current_user.id
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report

async def get_latest_report_for_inspection(db: AsyncSession, current_user: User, inspection_id: str) -> Report:
    # Authorize
    inspection = await get_inspection(db, current_user, inspection_id)
    
    query = select(Report).where(Report.inspection_id == inspection.id).order_by(Report.version.desc())
    result = await db.execute(query)
    report = result.scalars().first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found for this inspection")
        
    return report
