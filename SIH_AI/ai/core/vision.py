import os
import filetype
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, UnidentifiedImageError
from typing import Tuple
from schemas.vision import (
    ImageFormat, ImageQualityStatus, ImageQualityMetrics, 
    ImageValidationResult, PreprocessingConfig, PreprocessingResult
)
from core.logging import log_event

# Limits
MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB
MIN_IMAGE_DIMENSION = 200

# Supported Mime Types map
SUPPORTED_MIMES = {
    "image/jpeg": ImageFormat.JPEG,
    "image/png": ImageFormat.PNG,
    "image/webp": ImageFormat.WEBP
}

def validate_image(file_path: str) -> ImageValidationResult:
    """
    Validates an image file's structural integrity, format, and dimensions.
    Does NOT modify the image.
    """
    log_event("validate_image_start", file_path=file_path)
    
    if not os.path.exists(file_path):
        return ImageValidationResult(
            is_valid=False, format=ImageFormat.UNKNOWN, size_bytes=0, error_message="File not found"
        )
        
    size_bytes = os.path.getsize(file_path)
    if size_bytes > MAX_IMAGE_SIZE_BYTES:
        return ImageValidationResult(
            is_valid=False, format=ImageFormat.UNKNOWN, size_bytes=size_bytes, 
            error_message=f"File exceeds maximum size of {MAX_IMAGE_SIZE_BYTES} bytes"
        )
        
    # Check mime type safely using filetype
    kind = filetype.guess(file_path)
    if kind is None or kind.mime not in SUPPORTED_MIMES:
        mime = kind.mime if kind else "unknown"
        return ImageValidationResult(
            is_valid=False, format=ImageFormat.UNKNOWN, mime_type=mime, size_bytes=size_bytes,
            error_message=f"Unsupported format. Mime type: {mime}"
        )
        
    img_format = SUPPORTED_MIMES[kind.mime]
    
    try:
        # Load safely with Pillow
        with Image.open(file_path) as img:
            img.verify()  # verify checks file integrity without loading pixels
            
        # We must reopen to get actual dimensions cleanly if verify was used
        with Image.open(file_path) as img:
            width, height = img.size
            
            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                return ImageValidationResult(
                    is_valid=False, format=img_format, mime_type=kind.mime,
                    width=width, height=height, size_bytes=size_bytes,
                    error_message=f"Image dimensions ({width}x{height}) below minimum of {MIN_IMAGE_DIMENSION}px"
                )
                
            log_event("validate_image_success", file_path=file_path)
            return ImageValidationResult(
                is_valid=True, format=img_format, mime_type=kind.mime,
                width=width, height=height, size_bytes=size_bytes
            )
            
    except UnidentifiedImageError:
        return ImageValidationResult(
            is_valid=False, format=img_format, mime_type=kind.mime, size_bytes=size_bytes,
            error_message="Image file is corrupted and cannot be read"
        )
    except Exception as e:
        return ImageValidationResult(
            is_valid=False, format=img_format, mime_type=kind.mime, size_bytes=size_bytes,
            error_message=f"Unexpected validation error: {str(e)}"
        )

def assess_image_quality(file_path: str) -> ImageQualityMetrics:
    """
    Computes basic quality metrics: blur, brightness, contrast.
    """
    try:
        with Image.open(file_path) as img:
            # Reorient based on EXIF to get true properties
            img = ImageOps.exif_transpose(img)
            width, height = img.size
            resolution = width * height
            
            # Convert to grayscale for metric calculations
            gray = img.convert('L')
            arr = np.array(gray, dtype=np.float32)
            
            brightness = float(np.mean(arr))
            contrast = float(np.std(arr))
            
            # Simple discrete Laplacian for blur detection
            # Fast and doesn't require cv2
            if arr.shape[0] > 2 and arr.shape[1] > 2:
                lap = np.abs(
                    arr[1:-1, 1:-1]*4 
                    - arr[0:-2, 1:-1] 
                    - arr[2:, 1:-1] 
                    - arr[1:-1, 0:-2] 
                    - arr[1:-1, 2:]
                )
                blur_score = float(np.var(lap))
            else:
                blur_score = 0.0

            # Determine subjective status
            status = ImageQualityStatus.GOOD
            if blur_score < 100.0 or contrast < 20.0:
                status = ImageQualityStatus.POOR
            elif blur_score < 300.0 or contrast < 40.0:
                status = ImageQualityStatus.DEGRADED
                
            return ImageQualityMetrics(
                status=status,
                resolution_px=resolution,
                blur_score=blur_score,
                brightness=brightness,
                contrast=contrast,
                orientation_exif=None  # Stripped by exif_transpose logic internally
            )
    except Exception:
        return ImageQualityMetrics(
            status=ImageQualityStatus.INCONCLUSIVE,
            resolution_px=0
        )

def preprocess_image(original_path: str, output_path: str, config: PreprocessingConfig) -> PreprocessingResult:
    """
    Creates a processed derivative of the original image based on config.
    Original image is never overwritten.
    """
    log_event("preprocess_image_start", original=original_path, output=output_path)
    operations = []
    
    if not os.path.exists(original_path):
        return PreprocessingResult(success=False, original_path=original_path, error_message="Original image missing")
        
    try:
        with Image.open(original_path) as img:
            orig_dim = list(img.size)
            
            # Ensure we're in RGB mode to save nicely as jpeg/png later
            if img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # 1. Orientation
            if config.correct_orientation:
                img = ImageOps.exif_transpose(img)
                if list(img.size) != orig_dim:
                    operations.append("exif_transpose")
                    
            # 2. Upscale
            if config.upscale_factor > 1.0:
                w, h = img.size
                new_w, new_h = int(w * config.upscale_factor), int(h * config.upscale_factor)
                img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                operations.append(f"upscale_{config.upscale_factor}")

            # 3. Resize
            if config.max_dimension:
                w, h = img.size
                if w > config.max_dimension or h > config.max_dimension:
                    img.thumbnail((config.max_dimension, config.max_dimension), Image.Resampling.LANCZOS)
                    operations.append(f"resize_max_{config.max_dimension}")
                    
            # 3. Grayscale
            if config.apply_grayscale:
                img = img.convert('L')
                operations.append("grayscale")
                
            # 4. Denoise (Median filter)
            if config.apply_denoise:
                img = img.filter(ImageFilter.MedianFilter(size=3))
                operations.append("denoise_median")
                
            # 5. Contrast Enhancement
            if config.apply_contrast_enhancement:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.2)  # boost 20%
                operations.append("contrast_enhance_1.2")
                
            # Save derivative
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            img.save(output_path, quality=90, optimize=True)
            proc_dim = list(img.size)
            
        log_event("preprocess_image_success", original=original_path, output=output_path, operations=operations)
        return PreprocessingResult(
            success=True,
            original_path=original_path,
            processed_path=output_path,
            original_dimensions=orig_dim,
            processed_dimensions=proc_dim,
            operations_applied=operations
        )
        
    except Exception as e:
        log_event("preprocess_image_error", original=original_path, error=str(e))
        return PreprocessingResult(
            success=False, 
            original_path=original_path, 
            error_message=f"Preprocessing failed: {str(e)}"
        )
