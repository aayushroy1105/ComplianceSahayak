import os
import io
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from main import app
from core.config import settings
from api.errors import AIAPIException
from schemas.rag import RetrievalResult, RetrievedChunk, RetrievalMode
from schemas.applicability import ApplicabilityResult

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def create_mock_image_bytes():
    img = Image.new("RGB", (800, 600), "blue")
    draw = ImageDraw.Draw(img)
    draw.text((10, 10), "Test Label", fill="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()

def get_test_files():
    return {"image": ("test.jpg", create_mock_image_bytes(), "image/jpeg")}

@pytest.fixture(autouse=True)
def mock_quality():
    from core.vision import ImageQualityMetrics, ImageQualityStatus
    with patch("api.routes.assess_image_quality") as mock_assess:
        mock_assess.return_value = ImageQualityMetrics(blur_score=500.0, contrast_score=100.0, resolution_px=480000, brightness=128.0, status=ImageQualityStatus.GOOD)
        yield mock_assess

@pytest.fixture(autouse=True)
def setup_teardown():
    old_mock = settings.MOCK_AI
    settings.MOCK_AI = False
    yield
    settings.MOCK_AI = old_mock


# Test 1: MOCK_AI=true behavior
def test_mock_ai_flag(client):
    settings.MOCK_AI = True
    payload = {"scan_id": "TEST-MOCK"}
    response = client.post("/ai/analyze", data=payload, files=get_test_files())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["compliance"]["status"] == "INCONCLUSIVE"
    assert data["model_info"]["ocr_version"] == "mock"

# Test 2: Valid Compliant Pipeline
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
@patch("services.rag.retriever.Retriever.retrieve")
def test_valid_compliant_pipeline(mock_retrieve, mock_extract_text, client):
    # Setup OCR mock to return blocks that parse to all required fields for LM-005
    mock_extract_text.return_value = {
        "success": True,
        "text_blocks": [
            {"text": "MRP Rs. 100.00 (incl of all taxes)", "bounding_box": [0,0,1,1], "confidence": 0.99},
            {"text": "Net Quantity: 1 kg", "bounding_box": [0,0,1,1], "confidence": 0.99},
            {"text": "Mfd by: Acme Corp, India", "bounding_box": [0,0,1,1], "confidence": 0.99},
            {"text": "Retail package", "bounding_box": [0,0,1,1], "confidence": 0.99}
        ]
    }
    
    # Setup Retriever mock to return the relevant LM-005 rule chunk
    mock_retrieve.return_value = RetrievalResult(
        query="test query",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[
            RetrievedChunk(
                rule_id="LM-005",
                text="Every package shall bear MRP, Net Quantity, and Manufacturer.",
                score=0.9,
                source_document="Rules",
                source_section="Rule 6",
                corpus_hash="hash",
                chunk_index=0
            )
        ],
        corpus_hash="hash"
    )
    
    # We also mock context classifier to ensure it triggers retail
    with patch("services.classification.context_classifier.ContextClassifier.classify") as mock_context:
        from schemas.base import PackageContext
        mock_context.return_value = PackageContext(
            package_context="RETAIL",
            context_confidence=0.99,
            relevant_metadata={}
        )
        
        payload = {"scan_id": "TEST-COMPLIANT"}
        response = client.post("/ai/analyze", data=payload, files=get_test_files())
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Since MRP, Net Qty, and Mfg are present, Rule Engine should evaluate LM-005 as COMPLIANT
        assert data["compliance"]["status"] == "COMPLIANT"
        assert len(data["violations"]) == 0

# Test 3: Controlled Missing MRP (NON_COMPLIANT + LLM)
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
@patch("services.rag.retriever.Retriever.retrieve")
@patch("ai.services.llm.mock_provider.MockLLMProvider.generate")
def test_missing_mrp_pipeline(mock_generate, mock_retrieve, mock_extract_text, client):
    # Setup OCR mock missing MRP
    mock_extract_text.return_value = {
        "success": True,
        "text_blocks": [
            {"text": "Net Quantity: 1 kg", "bounding_box": [0,0,1,1], "confidence": 0.99},
            {"text": "Mfd by: Acme Corp", "bounding_box": [0,0,1,1], "confidence": 0.99},
        ]
    }
    
    mock_retrieve.return_value = RetrievalResult(
        query="test query",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="Requires MRP", score=0.9, source_document="x", source_section="y", corpus_hash="z", chunk_index=0)],
        corpus_hash="z"
    )
    
    mock_generate.return_value = '{"violation_reference": "MISSING_MRP", "action_text": "Please print MRP."}'
    
    with patch("services.classification.context_classifier.ContextClassifier.classify") as mock_context:
        from schemas.base import PackageContext
        mock_context.return_value = PackageContext(package_context="RETAIL", context_confidence=0.99, relevant_metadata={})
        
        payload = {"scan_id": "TEST-NONCOMPLIANT"}
        response = client.post("/ai/analyze", data=payload, files=get_test_files())
        
        assert response.status_code == 200
        data = response.json()
        assert data["compliance"]["status"] == "NON_COMPLIANT"
        assert any(v["violation_code"] == "MISSING_MRP" for v in data["violations"])
        assert len(data["corrective_actions"]) > 0
        assert data["corrective_actions"][0]["violation_reference"] == "MISSING_MRP"

# Test 4: OCR Failure -> INCONCLUSIVE
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
def test_ocr_failure(mock_extract_text, client):
    mock_extract_text.side_effect = AIAPIException(category="OCR_FAILURE", detail="Timeout")
    
    payload = {"scan_id": "TEST-OCR-FAIL"}
    response = client.post("/ai/analyze", data=payload, files=get_test_files())
    
    assert response.status_code == 200
    data = response.json()
    assert data["compliance"]["status"] == "INCONCLUSIVE"
    assert data["review_reason"] == "OCR_UNCERTAIN"

# Test 5: Applicability Uncertainty -> INCONCLUSIVE
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
def test_applicability_uncertain(mock_extract_text, client):
    mock_extract_text.return_value = {"success": True, "text_blocks": [{"text": "Unknown junk", "bounding_box": [0,0,1,1], "confidence": 0.5}]}
    
    with patch("services.applicability.engine.ApplicabilityEngine.evaluate") as mock_eval:
        mock_eval.return_value = ApplicabilityResult(status="INSUFFICIENT_CONTEXT", applicable_rule_ids=[], candidate_rule_ids=[])
        
        payload = {"scan_id": "TEST-APP-FAIL"}
        response = client.post("/ai/analyze", data=payload, files=get_test_files())
        
        assert response.status_code == 200
        data = response.json()
        assert data["compliance"]["status"] == "INCONCLUSIVE"
        assert data["review_reason"] == "LEGAL_CONTEXT_INSUFFICIENT" or data["review_reason"] == "INSUFFICIENT_EVIDENCE" or "INSUFFICIENT" in data["review_reason"]

# Test 6: RAG Unavailable -> safe INCONCLUSIVE
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
@patch("services.rag.retriever.Retriever.retrieve")
def test_rag_unavailable(mock_retrieve, mock_extract_text, client):
    mock_extract_text.return_value = {"success": True, "text_blocks": [{"text": "Retail package", "bounding_box": [0,0,1,1], "confidence": 0.99}]}
    
    # Simulate Vector Store error
    mock_retrieve.return_value = RetrievalResult(
        query="test query",
        retrieval_mode=RetrievalMode.REVIEW_ONLY,
        chunks=[],
        corpus_hash="z",
        error="VECTOR_STORE_ERROR"
    )
    
    with patch("services.classification.context_classifier.ContextClassifier.classify") as mock_context:
        from schemas.base import PackageContext
        mock_context.return_value = PackageContext(package_context="RETAIL", context_confidence=0.99, relevant_metadata={})
        
        payload = {"scan_id": "TEST-RAG-FAIL"}
        response = client.post("/ai/analyze", data=payload, files=get_test_files())
        
        assert response.status_code == 200
        data = response.json()
        assert data["compliance"]["status"] == "INCONCLUSIVE"
        # Since applicability was RETAIL (requires LM-005), but RAG returned no context, rule engine yields inconclusive

# Test 7: LLM Failure preserves Rule Engine Result
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
@patch("services.rag.retriever.Retriever.retrieve")
@patch("ai.services.llm.mock_provider.MockLLMProvider.generate")
def test_llm_failure_preserves_result(mock_generate, mock_retrieve, mock_extract_text, client):
    mock_extract_text.return_value = {"success": True, "text_blocks": [{"text": "Net Quantity: 1 kg", "bounding_box": [0,0,1,1], "confidence": 0.99}]}
    mock_retrieve.return_value = RetrievalResult(
        query="test query",
        retrieval_mode=RetrievalMode.AUTOMATIC,
        chunks=[RetrievedChunk(rule_id="LM-005", text="Requires MRP", score=0.9, source_document="x", source_section="y", corpus_hash="z", chunk_index=0)],
        corpus_hash="z"
    )
    
    # LLM throws an exception
    mock_generate.side_effect = Exception("Simulated LLM Timeout")
    
    with patch("services.classification.context_classifier.ContextClassifier.classify") as mock_context:
        from schemas.base import PackageContext
        mock_context.return_value = PackageContext(package_context="RETAIL", context_confidence=0.99, relevant_metadata={})
        
        payload = {"scan_id": "TEST-LLM-FAIL"}
        response = client.post("/ai/analyze", data=payload, files=get_test_files())
        
        assert response.status_code == 200
        data = response.json()
        # Authoritative result is preserved
        assert data["compliance"]["status"] == "NON_COMPLIANT"
        assert len(data["violations"]) > 0
        # But no corrective actions are generated
        assert len(data["corrective_actions"]) == 0

# Test 8: Verify AnalyzeResponse conforms to Schema
@patch("clients.ocr_client.OCRClient.extract_text", new_callable=AsyncMock)
def test_response_schema_compliance(mock_extract_text, client):
    mock_extract_text.return_value = {"success": True, "text_blocks": []}
    payload = {"scan_id": "TEST-SCHEMA"}
    response = client.post("/ai/analyze", data=payload, files=get_test_files())
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "scan_id" in data
    assert "product" in data
    assert "package_context" in data
    assert "declarations" in data
    assert "applicability" in data
    assert "compliance" in data
    assert "violations" in data
    assert "corrective_actions" in data
    assert "legal_references" in data
    assert "evidence" in data
    assert "review_required" in data
    assert "review_reason" in data
    assert "model_info" in data

# Test 9: Image Validation Failure
def test_image_validation_failure(client):
    # Pass an invalid file format (text as image)
    payload = {"scan_id": "TEST-INVALID-IMG"}
    files = {"image": ("dummy.txt", io.BytesIO(b"this is not an image"), "text/plain")}
    response = client.post("/ai/analyze", data=payload, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["compliance"]["status"] == "INCONCLUSIVE"
    assert data["review_reason"] == "INVALID_IMAGE"

# Test 10: Image Quality POOR
@patch("api.routes.assess_image_quality")
def test_image_quality_poor(mock_assess, client):
    from core.vision import ImageQualityMetrics, ImageQualityStatus
    mock_assess.return_value = ImageQualityMetrics(blur_score=10.0, contrast_score=10.0, resolution_px=1000, brightness=128.0, status=ImageQualityStatus.POOR)
    
    payload = {"scan_id": "TEST-POOR-IMG"}
    response = client.post("/ai/analyze", data=payload, files=get_test_files())
    assert response.status_code == 200
    data = response.json()
    assert data["compliance"]["status"] == "INCONCLUSIVE"
    assert data["review_reason"] == "LOW_IMAGE_QUALITY"

