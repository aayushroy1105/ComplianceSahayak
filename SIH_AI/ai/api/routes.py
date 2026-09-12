import tempfile
import os
import shutil
from fastapi import APIRouter, Depends, Form, UploadFile, File, Request
from typing import Optional, List
from schemas.base import AnalyzeResponse, ModelInfo, Product, PackageContext, Applicability, Compliance, Violation, Evidence
from core.config import settings
from core.logging import log_event
from api.errors import AIAPIException
from core.vision import validate_image, assess_image_quality, preprocess_image, PreprocessingConfig, ImageQualityStatus
from api.dependencies import (
    get_ocr_client, get_extractor, get_product_classifier,
    get_context_classifier, get_applicability_engine,
    get_retriever, get_rule_engine, get_llm_generator
)

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    app = request.app
    
    legal_index_ready = False
    if hasattr(app.state, 'indexer'):
        try:
            # Perform a lightweight query or status check to confirm index is alive and queryable
            legal_index_ready = app.state.indexer.health_check()
        except Exception as e:
            legal_index_ready = False
            
    log_event("health_check", status="OK", legal_index_ready=legal_index_ready)
    return {
        "status": "ok", 
        "service": settings.PROJECT_NAME, 
        "version": settings.VERSION,
        "legal_index_ready": legal_index_ready
    }

@router.post("/ai/analyze", response_model=AnalyzeResponse)
async def analyze_package(
    request: Request,
    scan_id: str = Form(...),
    images: List[UploadFile] = File(None),
    metadata: Optional[str] = Form(None),
    ocr_client = Depends(get_ocr_client),
    extractor = Depends(get_extractor),
    product_classifier = Depends(get_product_classifier),
    context_classifier = Depends(get_context_classifier),
    applicability_engine = Depends(get_applicability_engine),
    retriever = Depends(get_retriever),
    rule_engine = Depends(get_rule_engine),
    llm_generator = Depends(get_llm_generator)
):
    log_event("analyze_package_start", scan_id=scan_id)
    
    if not scan_id:
        log_event("analyze_package_error", reason="missing_scan_id")
        raise AIAPIException(category="INVALID_REQUEST", detail="scan_id is required")

    if not images or len(images) == 0:
        log_event("analyze_package_error", reason="missing_image")
        raise AIAPIException(category="INVALID_IMAGE", detail="at least one image file is required")

    # MOCK MODE BYPASS
    if settings.MOCK_AI:
        log_event("analyze_package_mock", scan_id=scan_id)
        response = AnalyzeResponse(
            success=True,
            scan_id=scan_id,
            product=Product(
                product_name="Unknown", 
                product_category="mock_category", 
                classification_confidence=0.99
            ),
            package_context=PackageContext(
                package_context="mock_context", 
                context_confidence=0.99,
                relevant_metadata={}
            ),
            declarations=[],
            applicability=Applicability(status="REVIEW_REQUIRED", applicable_rule_ids=[]),
            compliance=Compliance(status="INCONCLUSIVE"),
            violations=[],
            corrective_actions=[],
            legal_references=[],
            evidence=[],
            review_required=True,
            review_reason="LOW_IMAGE_QUALITY",
            model_info=ModelInfo(
                ocr_version="mock",
                classification_model_version="mock",
                embedding_model_version="mock",
                llm_version="mock",
                rag_version="mock",
                rule_engine_version="mock",
                legal_corpus_version="mock"
            )
        )
        log_event("analyze_package_complete", scan_id=scan_id, mock=True)
        return response

    # REAL PIPELINE ORCHESTRATION
    # Check index readiness first
    legal_index_ready = False
    if hasattr(request.app.state, 'indexer'):
        try:
            legal_index_ready = request.app.state.indexer.health_check()
        except Exception:
            pass
            
    if not legal_index_ready:
        log_event("analyze_package_error", reason="legal_index_unavailable")
        return AnalyzeResponse(
            success=False,
            scan_id=scan_id,
            product=Product(product_name="Unknown", product_category="Unknown", classification_confidence=0.0),
            package_context=PackageContext(package_context="Unknown", context_confidence=0.0, relevant_metadata={}),
            declarations=[],
            applicability=Applicability(status="REVIEW_REQUIRED", applicable_rule_ids=[]),
            compliance=Compliance(status="INCONCLUSIVE"),
            violations=[],
            corrective_actions=[],
            legal_references=[],
            evidence=[],
            review_required=True,
            review_reason="LEGAL_CONTEXT_INSUFFICIENT",
            model_info=ModelInfo(
                ocr_version="v1",
                classification_model_version="v1",
                embedding_model_version="v1",
                llm_version="v1",
                rag_version="v1",
                rule_engine_version="v1",
                legal_corpus_version="v1"
            )
        )

    temp_paths = []
    processed_paths = []
    all_ocr_blocks = []
    
    try:
        # Loop through all provided images
        for img_idx, img in enumerate(images):
            fd, temp_path = tempfile.mkstemp(suffix=".jpg")
            temp_paths.append(temp_path)
            
            # A. File Handling & Vision (Phase 2)
            with os.fdopen(fd, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)
                
            val_res = validate_image(temp_path)
            if not val_res.is_valid:
                log_event("image_validation_failed", scan_id=scan_id, image_idx=img_idx, error=val_res.error_message)
                continue # Skip invalid images rather than failing the whole inspection
                
            qual_res = assess_image_quality(temp_path)
            if qual_res.status == ImageQualityStatus.POOR:
                log_event("image_quality_poor", scan_id=scan_id, image_idx=img_idx)
                # We can still try OCR, but confidence might be lower
                
            prep_config = PreprocessingConfig(max_dimension=1920, upscale_factor=1.0, apply_grayscale=False, apply_contrast_enhancement=True)
            processed_path = temp_path + f"_processed_{img_idx}.jpg"
            processed_paths.append(processed_path)
            prep_res = preprocess_image(temp_path, processed_path, prep_config)
            
            target_image_path = processed_path if prep_res.success else temp_path

            # B. OCR (Phase 3)
            try:
                ocr_result = await ocr_client.extract_text(target_image_path, scan_id)
                blocks = ocr_result.get("text_blocks", [])
                
                # Vertical Text Fallback: If OCR is nearly empty OR missing critical tokens (MRP, Date)
                import re
                horizontal_text = " ".join([b.get("text", "") for b in blocks])
                needs_rotation = False
                
                # Token-aware checks for MRP and Dates
                mrp_pattern = re.compile(r'\b(m\.?r\.?p\.?|rs\.?|₹|inr)\b', re.IGNORECASE)
                date_pattern = re.compile(r'\b(exp|expiry|mf|mfg|mfd)\b', re.IGNORECASE)
                
                if not mrp_pattern.search(horizontal_text) or not date_pattern.search(horizontal_text):
                    needs_rotation = True
                    
                if len(blocks) < 3 or needs_rotation:
                    try:
                        from PIL import Image, ImageEnhance
                        with Image.open(target_image_path) as im:
                            w, h = im.size
                            
                            # RIGHT EDGE CROP (25%) -> Rotate 270
                            right_box = (int(w * 0.75), 0, w, h)
                            right_edge = im.crop(right_box)
                            right_edge = right_edge.resize((right_edge.width * 2, right_edge.height * 2), Image.Resampling.LANCZOS)
                            right_edge = ImageEnhance.Contrast(right_edge).enhance(1.5)
                            right_edge = ImageEnhance.Sharpness(right_edge).enhance(2.0)
                            right_rot = right_edge.transpose(Image.ROTATE_270)
                            right_path = target_image_path + "_right_rot.jpg"
                            right_rot.save(right_path)
                            temp_paths.append(right_path)
                            
                            # LEFT EDGE CROP (25%) -> Rotate 90
                            left_box = (0, 0, int(w * 0.25), h)
                            left_edge = im.crop(left_box)
                            left_edge = left_edge.resize((left_edge.width * 2, left_edge.height * 2), Image.Resampling.LANCZOS)
                            left_edge = ImageEnhance.Contrast(left_edge).enhance(1.5)
                            left_edge = ImageEnhance.Sharpness(left_edge).enhance(2.0)
                            left_rot = left_edge.transpose(Image.ROTATE_90)
                            left_path = target_image_path + "_left_rot.jpg"
                            left_rot.save(left_path)
                            temp_paths.append(left_path)
                            
                        ocr_right = await ocr_client.extract_text(right_path, scan_id)
                        ocr_left = await ocr_client.extract_text(left_path, scan_id)
                        
                        fallback_blocks = ocr_right.get("text_blocks", []) + ocr_left.get("text_blocks", [])
                        
                        existing_texts = set([re.sub(r'[^a-z0-9]', '', b.get("text", "").lower()) for b in blocks])
                        for fb in fallback_blocks:
                            norm_fb = re.sub(r'[^a-z0-9]', '', fb.get("text", "").lower())
                            if len(norm_fb) > 2 and norm_fb not in existing_texts:
                                blocks.append(fb)
                                
                    except Exception as fallback_e:
                        log_event("ocr_fallback_rotation_error", detail=str(fallback_e))

                all_ocr_blocks.extend(blocks)
            except AIAPIException as e:
                if e.category == "OCR_FAILURE":
                    log_event("ocr_failure_mapped", scan_id=scan_id, image_idx=img_idx, detail=e.detail)
                    continue
                raise e

        if not all_ocr_blocks:
            log_event("ocr_failure_all_images", scan_id=scan_id)
            return _build_inconclusive_response(scan_id, "OCR_UNCERTAIN")
            
        # C. Extraction & Classification (Phase 4 & 5)
        declarations = extractor.extract(all_ocr_blocks, image_id=scan_id)
        product = product_classifier.classify(declarations, all_ocr_blocks)
        package_context = context_classifier.classify(declarations, all_ocr_blocks)
        
        # D. Applicability (Phase 6)
        applicability = applicability_engine.evaluate(product, package_context)
        
        # E. RAG Retrieval (Phase 7)
        # We query based on product/context to get relevant semantic matches, filtered by applicability
        query = f"Rules for {product.product_category} {package_context.package_context}"
        retrieval = retriever.retrieve(query=query, applicability_result=applicability, k=5)
        
        # F. Rule Engine (Phase 8)
        compliance, violations, evidence, rev_req, rev_reason = rule_engine.evaluate(
            declarations=declarations,
            applicability=applicability,
            retrieval=retrieval,
            package_context=package_context
        )
        
        # G. LLM Advisory (Phase 9)
        corrective_actions = []
        if compliance.status == "NON_COMPLIANT":
            corrective_actions = llm_generator.generate_corrections(violations=violations, retrieval=retrieval)
            
        model_info = ModelInfo(
            ocr_version="v1.0",
            classification_model_version="v1.0",
            embedding_model_version="v1.0",
            llm_version="mock_v1",
            rag_version="v1.0",
            rule_engine_version="v1.0",
            legal_corpus_version="v1.0"
        )
        
        response = AnalyzeResponse(
            success=True,
            scan_id=scan_id,
            product=product.model_dump() if hasattr(product, 'model_dump') else product.dict(),
            package_context=package_context.model_dump() if hasattr(package_context, 'model_dump') else package_context.dict(),
            declarations=[d.model_dump() if hasattr(d, 'model_dump') else d.dict() for d in declarations],
            applicability={"status": "REVIEW_REQUIRED" if applicability.status == "INSUFFICIENT_CONTEXT" else applicability.status, "applicable_rule_ids": applicability.applicable_rule_ids},
            compliance={"status": compliance.status},
            violations=[v.model_dump() if hasattr(v, 'model_dump') else v.dict() for v in violations],
            corrective_actions=[c.model_dump() if hasattr(c, 'model_dump') else c.dict() for c in corrective_actions],
            legal_references=[], # Could map from retrieval if needed, but keeping simple
            evidence=[e.model_dump() if hasattr(e, 'model_dump') else e.dict() for e in evidence],
            review_required=rev_req,
            review_reason=rev_reason,
            model_info=model_info,
            raw_ocr_blocks=all_ocr_blocks
        )
        
        log_event("analyze_package_complete", scan_id=scan_id, mock=False, compliance=compliance.status)
        return response

    finally:
        for p in temp_paths + processed_paths:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass


def _build_inconclusive_response(scan_id: str, review_reason: str) -> AnalyzeResponse:
    return AnalyzeResponse(
        success=True,
        scan_id=scan_id,
        product=Product(product_name="Unknown", product_category="UNKNOWN", classification_confidence=0.0),
        package_context=PackageContext(package_context="UNKNOWN", context_confidence=0.0, relevant_metadata={}),
        declarations=[],
        applicability=Applicability(status="REVIEW_REQUIRED", applicable_rule_ids=[], candidate_rule_ids=[]),
        compliance=Compliance(status="INCONCLUSIVE"),
        violations=[],
        corrective_actions=[],
        legal_references=[],
        evidence=[],
        review_required=True,
        review_reason=review_reason,
        model_info=ModelInfo(
            ocr_version="v1.0",
            classification_model_version="v1.0",
            embedding_model_version="v1.0",
            llm_version="mock_v1",
            rag_version="v1.0",
            rule_engine_version="v1.0",
            legal_corpus_version="v1.0"
        )
    )
