import httpx
import json
import asyncio
from typing import Optional, Dict, Any, List
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.ai_result import AIAnalyzeResponse, AIErrorResponse

class AIClientError(Exception):
    pass

class AIServiceUnavailableError(AIClientError):
    pass

class AIResponseInvalidError(AIClientError):
    def __init__(self, detail: str, validation_errors: Any = None):
        self.detail = detail
        self.validation_errors = validation_errors
        super().__init__(detail)

class AIAnalysisError(AIClientError):
    def __init__(self, error_category: str, error_detail: str):
        self.error_category = error_category
        self.error_detail = error_detail
        super().__init__(f"{error_category}: {error_detail}")

class AIServiceClient:
    def __init__(
        self,
        base_url: str = settings.AI_SERVICE_URL,
        mock_mode: bool = settings.MOCK_AI,
        connect_timeout: float = settings.AI_CONNECT_TIMEOUT,
        read_timeout: float = settings.AI_READ_TIMEOUT,
        max_retries: int = 2,
    ):
        self.base_url = base_url
        self.mock_mode = mock_mode
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.max_retries = max_retries
        self.timeout = httpx.Timeout(connect=connect_timeout, read=read_timeout, write=10.0, pool=10.0)

    async def check_health(self) -> bool:
        if self.mock_mode:
            return True
        try:
            import logging
            logger = logging.getLogger(__name__)
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    if not data.get("legal_index_ready", False):
                        logger.error("AI service healthy but LEGAL INDEX NOT READY")
                        return False
                    return True
                return False
        except Exception:
            return False

    async def analyze(
        self,
        images_data: List[tuple], # List of (filename, bytes, mime_type)
        scan_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AIAnalyzeResponse:
        if self.mock_mode:
            return self._generate_mock_response(scan_id)

        files = [("images", img) for img in images_data]
        data = {"scan_id": scan_id}
        if metadata:
            data["metadata"] = json.dumps(metadata)

        url = f"{self.base_url}/ai/analyze"
        backoff_seconds = [1, 2, 4]
        
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(url, files=files, data=data)
                    
                    if response.status_code in (502, 503, 429) and attempt < self.max_retries:
                        await asyncio.sleep(backoff_seconds[attempt])
                        continue
                        
                    return self._validate_response(response)
            except (httpx.ConnectError, httpx.ConnectTimeout) as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(backoff_seconds[attempt])
                    continue
                raise AIServiceUnavailableError(str(e))
            except httpx.ReadTimeout as e:
                raise AIServiceUnavailableError("Read timeout while waiting for AI service")
        
        raise AIServiceUnavailableError("Max retries exceeded")

    def _validate_response(self, response: httpx.Response) -> AIAnalyzeResponse:
        if response.status_code != 200:
            if response.status_code >= 500:
                raise AIResponseInvalidError(f"AI returned HTTP {response.status_code}")
            try:
                data = response.json()
            except ValueError:
                raise AIResponseInvalidError("Failed to parse error response as JSON")
            
            if not data.get("success", True):
                raise AIAnalysisError(
                    error_category=data.get("error_category", "UNKNOWN"),
                    error_detail=data.get("error_detail", "No details")
                )
            raise AIResponseInvalidError(f"Unexpected HTTP {response.status_code}")

        try:
            data = response.json()
        except ValueError:
            raise AIResponseInvalidError("Failed to parse response as JSON")
            
        if "success" not in data:
            raise AIResponseInvalidError("Missing 'success' field in response")
            
        if data["success"]:
            try:
                return AIAnalyzeResponse.model_validate(data)
            except ValidationError as e:
                raise AIResponseInvalidError(
                    detail=f"AI response failed schema validation: {e.error_count()} errors",
                    validation_errors=e.errors()
                )
        else:
            raise AIAnalysisError(
                error_category=data.get("error_category", "UNKNOWN_ERROR"),
                error_detail=data.get("error_detail", "No error detail provided")
            )

    async def health_check(self) -> bool:
        if self.mock_mode:
            return True
        try:
            async with httpx.AsyncClient(timeout=self.connect_timeout) as client:
                resp = await client.get(f"{self.base_url}/health")
                return resp.status_code == 200
        except Exception:
            return False

    def _generate_mock_response(self, scan_id: str) -> AIAnalyzeResponse:
        return AIAnalyzeResponse(
            success=True,
            scan_id=scan_id,
            product={
                "product_name": "Real Sample Biscuits",
                "product_category": "Food",
                "classification_confidence": 0.95,
                "signals": ["sweet", "baked"],
                "classification_method": "NLP_RULES"
            },
            package_context={
                "package_context": "retail packaging with barcode",
                "context_confidence": 0.9,
                "relevant_metadata": {}
            },
            declarations=[
                {
                    "field_name": "MRP",
                    "raw_value": "Rs 50",
                    "normalized_value": "50.00 INR",
                    "confidence": 0.98,
                    "extraction_status": "FOUND"
                },
                {
                    "field_name": "NET_QUANTITY",
                    "raw_value": "100g",
                    "normalized_value": "100.0",
                    "normalized_unit": "g",
                    "confidence": 0.85,
                    "extraction_status": "FOUND"
                }
            ],
            applicability={
                "status": "REVIEW_REQUIRED",
                "applicable_rule_ids": ["LM-001", "LM-010"]
            },
            compliance={
                "status": "NON_COMPLIANT"
            },
            violations=[
                {
                    "violation_code": "MISSING_QUANTITY",
                    "rule_id": "LM-010",
                    "severity": "HIGH",
                    "description": "Net quantity is not declared.",
                    "confidence": 0.99,
                    "evidence_references": ["EVID_001"]
                }
            ],
            corrective_actions=[
                {
                    "violation_reference": "MISSING_QUANTITY",
                    "action_text": "Add a clear net quantity declaration.",
                    "status": "GENERATED"
                }
            ],
            legal_references=[
                {
                    "rule_id": "LM-010",
                    "rule_number": "Rule 11",
                    "sub_rule": "1(a)",
                    "source_document": "1(1).pdf",
                    "legal_version": "2011",
                    "rule_version": "1.0"
                }
            ],
            evidence=[
                {
                    "evidence_id": "EVID_001",
                    "evidence_type": "MISSING_FIELD",
                    "declaration_reference": "NET_QUANTITY",
                    "rule_id": "LM-010",
                    "description": "System failed to find quantity."
                }
            ],
            review_required=True,
            review_reason="OCR_UNCERTAIN",
            model_info={}
        )
