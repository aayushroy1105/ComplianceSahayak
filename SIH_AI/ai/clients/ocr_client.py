import httpx
from typing import Dict, Any, Optional
from core.config import settings
from api.errors import AIAPIException
from core.logging import log_event

class OCRClient:
    def __init__(self):
        self.base_url = settings.OCR_SERVICE_URL.rstrip('/')
        self.timeout = settings.OCR_TIMEOUT
        
    async def extract_text(self, image_path: str, scan_id: str) -> Dict[str, Any]:
        """
        Sends an image to the isolated OCR service for text extraction.
        """
        log_event("ocr_client_request_start", scan_id=scan_id, url=self.base_url)
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                with open(image_path, "rb") as f:
                    files = {"image": (image_path.split('/')[-1], f, "image/jpeg")}
                    data = {"scan_id": scan_id}
                    
                    response = await client.post(
                        f"{self.base_url}/extract",
                        data=data,
                        files=files
                    )
                    
                response.raise_for_status()
                result = response.json()
                
                if not result.get("success"):
                    log_event("ocr_client_error", reason="unsuccessful_response", detail=result.get("error_message"))
                    raise AIAPIException(category="OCR_FAILURE", detail=result.get("error_message", "OCR service returned success=False"))
                    
                log_event("ocr_client_success", scan_id=scan_id, processing_time_ms=result.get("processing_time_ms"))
                return result
                
        except httpx.ConnectError:
            log_event("ocr_client_error", reason="connection_refused")
            raise AIAPIException(category="OCR_FAILURE", detail="Failed to connect to OCR service. Is it running?")
        except httpx.TimeoutException:
            log_event("ocr_client_error", reason="timeout")
            raise AIAPIException(category="OCR_FAILURE", detail=f"OCR service timed out after {self.timeout}s")
        except httpx.HTTPStatusError as e:
            log_event("ocr_client_error", reason="http_error", status_code=e.response.status_code)
            raise AIAPIException(category="OCR_FAILURE", detail=f"OCR service HTTP error: {e.response.status_code}")
        except Exception as e:
            log_event("ocr_client_error", reason="unexpected", detail=str(e))
            raise AIAPIException(category="OCR_FAILURE", detail=f"Unexpected OCR communication error: {str(e)}")
