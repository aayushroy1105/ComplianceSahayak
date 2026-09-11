import time
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import Optional
from app.schemas import ExtractResponse, TextBlock
from app.engine import ocr_engine

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "service": "ocr_engine",
        "model_initialized": getattr(ocr_engine, 'initialized', False)
    }

@router.post("/extract", response_model=ExtractResponse)
async def extract_text(
    scan_id: str = Form(None),
    request_id: str = Form(None),
    image: UploadFile = File(...)
):
    ident = scan_id or request_id
    if not ident:
        raise HTTPException(status_code=400, detail="Must provide scan_id or request_id")
        
    if not image:
        raise HTTPException(status_code=400, detail="Image is required")
        
    try:
        image_bytes = await image.read()
        blocks, processing_time_ms = ocr_engine.extract_text(image_bytes)
        
        # Convert dictionary blocks to Pydantic objects
        text_blocks = [TextBlock(**b) for b in blocks]
        
        return ExtractResponse(
            success=True,
            image_id=ident,
            text_blocks=text_blocks,
            ocr_model_version=ocr_engine.version,
            processing_time_ms=processing_time_ms,
            mock=False
        )
    except ValueError as e:
        # Invalid image processing failure
        return ExtractResponse(
            success=False,
            image_id=ident,
            text_blocks=[],
            ocr_model_version="error",
            processing_time_ms=0,
            mock=False,
            error_message=str(e)
        )
    except Exception as e:
        # General Inference failure
        return ExtractResponse(
            success=False,
            image_id=ident,
            text_blocks=[],
            ocr_model_version="error",
            processing_time_ms=0,
            mock=False,
            error_message=f"OCR Inference failed: {str(e)}"
        )
