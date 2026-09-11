from pydantic import BaseModel
from typing import List, Optional

class TextBlock(BaseModel):
    text: str
    confidence: float
    bbox: List[int]  # [x, y, w, h] or similar depending on final implementation

class ExtractResponse(BaseModel):
    success: bool
    image_id: str
    text_blocks: List[TextBlock]
    ocr_model_version: str
    processing_time_ms: int
    mock: bool = False
    error_message: Optional[str] = None
