import os
import aiofiles
import uuid
import logging
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.upload_dir = Path(settings.ABSOLUTE_UPLOAD_DIR)
        
        # Ensure upload dir exists
        if not self.upload_dir.exists():
            self.upload_dir.mkdir(parents=True, exist_ok=True)
            
    def _generate_safe_filename(self, original_filename: str) -> str:
        # Avoids path traversal and naming collisions
        ext = "".join(Path(original_filename).suffixes)[-1:] if Path(original_filename).suffixes else ""
        return f"{uuid.uuid4().hex}{ext}"
        
    async def save_file(self, file_content: bytes, original_filename: str) -> str:
        """
        Saves file locally and returns the relative storage path/key.
        """
        safe_filename = self._generate_safe_filename(original_filename)
        # Using forward slashes for cross-platform DB storage
        storage_path = f"{settings.UPLOAD_DIR}/{safe_filename}"
        
        # Actual OS path
        full_path = self.upload_dir / safe_filename
        
        async with aiofiles.open(full_path, 'wb') as f:
            await f.write(file_content)
            
        logger.info(f"File saved to {full_path}")
        return storage_path
        
    async def delete_file(self, storage_path: str) -> bool:
        """
        Deletes file if it exists. Returns True if deleted, False otherwise.
        """
        # Validate path to prevent directory traversal
        if not storage_path.startswith(f"{settings.UPLOAD_DIR}/"):
            logger.warning(f"Attempted to delete file outside upload dir: {storage_path}")
            return False
            
        # Extract just the filename part to be safe
        filename = Path(storage_path).name
        full_path = self.upload_dir / filename
        
        try:
            if full_path.exists() and full_path.is_file():
                os.remove(full_path)
                logger.info(f"Deleted file {full_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete file {full_path}: {str(e)}")
            return False

# Singleton instance
storage_service = StorageService()
