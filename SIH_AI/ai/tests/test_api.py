import os
from fastapi.testclient import TestClient
import pytest
import io

os.environ["MOCK_AI"] = "true"

from main import app
from core.config import settings

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "service" in response.json()

def test_ai_analyze_mock(client):
    # Simulate a multipart/form-data request
    payload = {"scan_id": "TEST-123"}
    files = {"image": ("dummy.jpg", io.BytesIO(b"fake_image_data"), "image/jpeg")}
    
    response = client.post("/ai/analyze", data=payload, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["scan_id"] == "TEST-123"
    assert "product" in data
    assert "package_context" in data
    assert "compliance" in data
    assert data["compliance"]["status"] == "INCONCLUSIVE"
    assert data["review_required"] is True
    assert data["review_reason"] == "LOW_IMAGE_QUALITY"
    assert "applicable_rule_ids" in data["applicability"]

def test_ai_analyze_missing_scan_id(client):
    # Test missing scan_id (FastAPI Form validation will fail with 422)
    files = {"image": ("dummy.jpg", io.BytesIO(b"fake_image_data"), "image/jpeg")}
    response = client.post("/ai/analyze", data={}, files=files)
    assert response.status_code == 422

def test_ai_analyze_missing_image(client):
    # Test missing image upload (should trigger INVALID_IMAGE 400 error handled by custom exception)
    payload = {"scan_id": "TEST-123"}
    response = client.post("/ai/analyze", data=payload)
    assert response.status_code == 400
    assert response.json()["error_category"] == "INVALID_IMAGE"

def test_ai_analyze_rag_unavailable(client, monkeypatch):
    import api.routes
    monkeypatch.setattr(api.routes.settings, "MOCK_AI", False)
    from main import app
    monkeypatch.setattr(app.state.indexer, "health_check", lambda: False)
    payload = {"scan_id": "TEST-RAG"}
    files = {"image": ("dummy.jpg", io.BytesIO(b"fake_image_data"), "image/jpeg")}
    
    response = client.post("/ai/analyze", data=payload, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert data["review_reason"] == "LEGAL_CONTEXT_INSUFFICIENT"
