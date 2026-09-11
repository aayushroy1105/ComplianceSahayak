from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ImageFormat(str, Enum):
    JPEG = "JPEG"
    PNG = "PNG"
    WEBP = "WEBP"
    UNKNOWN = "UNKNOWN"

class ImageQualityStatus(str, Enum):
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    POOR = "POOR"
    INCONCLUSIVE = "INCONCLUSIVE"

class ImageQualityMetrics(BaseModel):
    status: ImageQualityStatus
    resolution_px: int
    blur_score: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    orientation_exif: Optional[int] = None

class ImageValidationResult(BaseModel):
    is_valid: bool
    format: ImageFormat
    mime_type: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    size_bytes: int
    error_message: Optional[str] = None

class PreprocessingConfig(BaseModel):
    max_dimension: Optional[int] = 2048
    apply_grayscale: bool = False
    apply_denoise: bool = False
    apply_contrast_enhancement: bool = False
    correct_orientation: bool = True

class PreprocessingResult(BaseModel):
    success: bool
    original_path: str
    processed_path: Optional[str] = None
    original_dimensions: Optional[List[int]] = None
    processed_dimensions: Optional[List[int]] = None
    operations_applied: List[str] = []
    version: str = "v1"
    error_message: Optional[str] = None
