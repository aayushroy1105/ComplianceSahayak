from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import Optional, List
from fastapi import HTTPException
from uuid import UUID

from app.models.inspection import Inspection
from app.models.inspection_image import InspectionImage
from app.models.declaration import Declaration
from app.models.violation import Violation
from app.models.evidence import Evidence
from app.models.legal_reference import LegalReference
from app.models.corrective_action import CorrectiveAction
from app.models.audit_log import AuditLog
from app.models.manufacturer import Manufacturer
from app.models.product import Product
from app.models.officer import Officer

from app.schemas.ai_result import AIAnalyzeResponse
from app.clients.ai_client import AIServiceClient

async def process_inspection_analysis(
    db: AsyncSession,
    inspection_id: UUID,
    user_id: UUID,
    ai_client: AIServiceClient
) -> Inspection:
    
    # 1. Fetch inspection
    result = await db.execute(select(Inspection).where(Inspection.id == inspection_id))
    inspection = result.scalars().first()
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
        
    # Check status
    if inspection.review_status == "LOCKED":
        raise HTTPException(status_code=400, detail="Cannot analyze a locked inspection")
    if inspection.processing_status == "PROCESSING":
        raise HTTPException(status_code=409, detail="Inspection is already being processed")
        
    # Fetch an image (we'll pick the first valid image, FRONT preferred if available)
    img_res = await db.execute(select(InspectionImage).where(InspectionImage.inspection_id == inspection.id))
    images = img_res.scalars().all()
    if not images:
        raise HTTPException(status_code=400, detail="No images uploaded for this inspection")
        

    
    # 2. Update status to PROCESSING
    inspection.processing_status = "PROCESSING"
    await db.commit()
    await db.refresh(inspection)
    
    insp_id = inspection.id
    insp_code = inspection.inspection_code
    
    try:
        # 3. Read all image files from storage
        import os
        from app.core.config import settings
        
        images_data = []
        for img in images:
            file_path = img.storage_path
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.ABSOLUTE_UPLOAD_DIR, os.path.basename(file_path))
                
            with open(file_path, "rb") as f:
                image_bytes = f.read()
                
            images_data.append((
                img.original_filename or f"image_{img.image_type}.jpg",
                image_bytes,
                img.mime_type or "image/jpeg"
            ))
            
        # 4. Check RAG/AI readiness
        is_healthy = await ai_client.check_health()
        if not is_healthy:
            raise Exception("AI/RAG service is currently unavailable. Failing closed.")
            
        # 5. Call AI Client
        metadata = {}
        if inspection.location_text:
            metadata["location"] = inspection.location_text
            
        ai_response = await ai_client.analyze(
            images_data=images_data,
            scan_id=inspection.inspection_code,
            metadata=metadata
        )
        
        # 5. Persist Results (Idempotent cleanup first)
        await _cleanup_previous_analysis(db, inspection.id)
        
        import uuid as _uuid_mod

        # Build the set of valid image UUIDs for this inspection.
        # Only these are legitimate values for source_image_id.
        valid_image_ids = {img.id for img in images}

        def _resolve_source_image_id(raw_val):
            """Resolve the AI's source_image_id to a verified InspectionImage UUID.

            Returns the UUID if raw_val is a valid UUID that belongs to this
            inspection's image set.  Returns None otherwise — we must not
            fabricate an association to an arbitrary image.
            """
            if not raw_val:
                return None
            try:
                parsed = _uuid_mod.UUID(str(raw_val))
            except ValueError:
                # Not a UUID at all (e.g. inspection_code string).
                return None
            if parsed in valid_image_ids:
                return parsed
            # Valid UUID format but does not belong to this inspection's images.
            return None

        # Save Declarations
        for d in ai_response.declarations:
            db.add(Declaration(
                inspection_id=inspection.id,
                field_name=d.field_name,
                raw_value=d.raw_value,
                normalized_value=d.normalized_value,
                normalized_unit=d.normalized_unit,
                confidence=d.confidence,
                bounding_box=d.bounding_box,
                extraction_status=d.extraction_status,
                source_image_id=_resolve_source_image_id(d.source_image_id)
            ))
            
        # Save Legal References
        for lr in ai_response.legal_references:
            db.add(LegalReference(
                inspection_id=inspection.id,
                rule_id=lr.rule_id,
                rule_number=lr.rule_number,
                sub_rule=lr.sub_rule,
                schedule=lr.schedule,
                source_document=lr.source_document,
                legal_version=lr.legal_version,
                rule_version=lr.rule_version
            ))
            
        # Ensure OCR traceability
        import json
        ocr_text_content = ""
        if hasattr(ai_response, 'raw_ocr_blocks') and ai_response.raw_ocr_blocks:
            ocr_text_content = json.dumps(ai_response.raw_ocr_blocks)
        else:
            ocr_text_content = " ".join([e.ocr_text for e in ai_response.evidence if e.ocr_text])
            
        if ocr_text_content:
            from app.models.ocr_result import OCRResult
            ocr_record = OCRResult(
                inspection_id=inspection.id,
                image_id=images[0].id if images else None,
                full_text=ocr_text_content,
                confidence=ai_response.package_context.context_confidence if ai_response.package_context else 1.0,
                ocr_model_version=ai_response.model_info.ocr_version
            )
            db.add(ocr_record)
            
        # Evidence Mapping to keep track of generated UUIDs
        evidence_id_map = {}
        for e in ai_response.evidence:
            evidence_record = Evidence(
                inspection_id=inspection.id,
                image_id=images[0].id if images else None,
                evidence_id_ai=e.evidence_id,
                evidence_type=e.evidence_type,
                ocr_text=e.ocr_text,
                bounding_box=e.bounding_box,
                description=e.description,
                declaration_reference=e.declaration_reference,
                rule_id=e.rule_id
            )
            db.add(evidence_record)
            await db.flush() # get ID
            evidence_id_map[e.evidence_id] = evidence_record.id
            
        # Save Violations
        for v in ai_response.violations:
            violation_record = Violation(
                inspection_id=inspection.id,
                violation_code=v.violation_code,
                rule_id=v.rule_id,
                rule_version=v.rule_version,
                severity=v.severity,
                description=v.description,
                confidence=v.confidence,
                evidence_references=v.evidence_references
            )
            db.add(violation_record)
            await db.flush()
                    
            # Corrective Actions for this violation
            for ca in [c for c in ai_response.corrective_actions if c.violation_reference == v.violation_code]:
                db.add(CorrectiveAction(
                    inspection_id=inspection.id,
                    violation_id=violation_record.id,
                    violation_reference=ca.violation_reference,
                    action_text=ca.action_text,
                    status=ca.status
                ))
        
        # Update Inspection status
        inspection.processing_status = "COMPLETED"
        if ai_response.compliance.status == "COMPLIANT":
            inspection.compliance_status = "COMPLIANT"
        elif ai_response.compliance.status == "NON_COMPLIANT":
            inspection.compliance_status = "NON_COMPLIANT"
        else:
            inspection.compliance_status = "INCONCLUSIVE"
            
        if ai_response.review_required:
            inspection.review_status = "PENDING"  # PENDING review
        else:
            inspection.review_status = "NOT_REQUIRED"
            
        inspection.review_required = ai_response.review_required
        valid_review_reasons = {
            "LOW_IMAGE_QUALITY",
            "OCR_UNCERTAIN",
            "APPLICABILITY_UNCERTAIN",
            "CONFLICTING_INFORMATION",
            "PHYSICAL_VERIFICATION_REQUIRED",
            "LEGAL_CONTEXT_INSUFFICIENT",
            "INSUFFICIENT_EVIDENCE"
        }
        mapped_reason = ai_response.review_reason
        if mapped_reason and mapped_reason not in valid_review_reasons:
            if "IMAGE" in mapped_reason or "QUALITY" in mapped_reason:
                mapped_reason = "LOW_IMAGE_QUALITY"
            elif "OCR" in mapped_reason or "TEXT" in mapped_reason:
                mapped_reason = "OCR_UNCERTAIN"
            else:
                mapped_reason = "INSUFFICIENT_EVIDENCE"
        inspection.review_reason = mapped_reason
        inspection.applicability_status = ai_response.applicability.status
        inspection.applicable_rule_ids = ai_response.applicability.applicable_rule_ids
        
        # Product & Context
        inspection.product_name_ai = ai_response.product.product_name
        inspection.product_category_ai = ai_response.product.product_category
        inspection.classification_confidence = ai_response.product.classification_confidence
        inspection.signals = ai_response.product.signals
        inspection.classification_method = ai_response.product.classification_method
        
        inspection.package_context = ai_response.package_context.package_context
        inspection.context_confidence = ai_response.package_context.context_confidence
        inspection.relevant_metadata = ai_response.package_context.relevant_metadata
        
        # Link Manufacturer & Product Entities
        # Entity linking logic removed: Master entities must only be created via explicit verified paths, not directly from OCR.
        
        # Save Declarations, Evidence, etc. as before

        # Model versions metadata
        inspection.ocr_version = ai_response.model_info.ocr_version
        inspection.classification_model_version = ai_response.model_info.classification_model_version
        inspection.embedding_model_version = ai_response.model_info.embedding_model_version
        inspection.llm_version = ai_response.model_info.llm_version
        inspection.rag_version = ai_response.model_info.rag_version
        inspection.rule_engine_version = ai_response.model_info.rule_engine_version
        inspection.legal_corpus_version = ai_response.model_info.legal_corpus_version
        
        # Determine if LLM failure happened but Rule Engine worked
        # (This logic is implicitly handled as we persist compliance_status as it comes from AI, and corrective_actions will just be empty)
        
        await db.commit()
        await db.refresh(inspection)
        
        # Audit log
        db.add(AuditLog(
            inspection_id=inspection.id,
            user_id=user_id,
            action="AI_ANALYSIS_COMPLETED",
            metadata_col={"scan_id": inspection.inspection_code, "compliance": ai_response.compliance.status}
        ))
        await db.commit()
        
        return inspection

    except Exception as e:
        import traceback
        traceback.print_exc()
        # Failure path
        await db.rollback()
        
        from sqlalchemy import update
        await db.execute(
            update(Inspection)
            .where(Inspection.id == insp_id)
            .values(processing_status="FAILED")
        )
        
        db.add(AuditLog(
            inspection_id=insp_id,
            user_id=user_id,
            action="AI_ANALYSIS_FAILED",
            metadata_col={"scan_id": insp_code, "error": str(e)}
        ))
        await db.commit()
        raise HTTPException(status_code=502, detail=f"AI Analysis Failed: {str(e)}")

async def _cleanup_previous_analysis(db: AsyncSession, inspection_id: UUID):
    # Declarations
    await db.execute(delete(Declaration).where(Declaration.inspection_id == inspection_id))
    # Violations & Evidence mapping
    v_res = await db.execute(select(Violation).where(Violation.inspection_id == inspection_id))
    violations = v_res.scalars().all()
    for v in violations:
        await db.execute(delete(CorrectiveAction).where(CorrectiveAction.violation_id == v.id))
        
    await db.execute(delete(Violation).where(Violation.inspection_id == inspection_id))
    await db.execute(delete(Evidence).where(Evidence.inspection_id == inspection_id))
    await db.execute(delete(LegalReference).where(LegalReference.inspection_id == inspection_id))
    
    from app.models.ocr_result import OCRResult
    await db.execute(delete(OCRResult).where(OCRResult.inspection_id == inspection_id))
    
    await db.flush()
