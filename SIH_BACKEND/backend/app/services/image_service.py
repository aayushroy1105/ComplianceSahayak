import io
from PIL import Image
from fastapi import HTTPException
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# To prevent decompression bomb attacks
Image.MAX_IMAGE_PIXELS = 100_000_000 

def validate_image_file(file_content: bytes, original_filename: str, content_type: str) -> dict:
    """
    Validates file size, extension, MIME type, and checks if it's a valid image using PIL.
    Returns extracted metadata or raises HTTPException.
    """
    # 1. Validate size
    max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
    if len(file_content) > max_size_bytes:
        raise HTTPException(status_code=400, detail=f"File size exceeds maximum limit of {settings.MAX_IMAGE_SIZE_MB}MB.")
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="File is empty.")

    # 2. Validate MIME type & Extension
    if content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported MIME type: {content_type}.")
        
    ext = "." + original_filename.split(".")[-1].lower() if "." in original_filename else ""
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file extension: {ext}.")

    # 3. Validate image integrity and dimensions using Pillow
    try:
        with Image.open(io.BytesIO(file_content)) as img:
            img.verify() # Verify that it is, in fact, an image
            
            # Since verify() doesn't return width/height reliably in all versions without a load,
            # we open again to get dimensions if needed (verify leaves file pointer at end)
        with Image.open(io.BytesIO(file_content)) as img:
            width, height = img.size
            img_format = img.format # e.g. 'JPEG', 'PNG'
            
            # Additional safety: check dimensions
            if width < 10 or height < 10:
                raise HTTPException(status_code=400, detail="Image dimensions are too small.")
                
            return {
                "width": width,
                "height": height,
                "format": img_format,
                "file_size": len(file_content)
            }
    except Exception as e:
        logger.warning(f"Invalid image file uploaded: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid or corrupted image file.")
