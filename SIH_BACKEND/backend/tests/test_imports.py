import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_app_import():
    import app
    assert app is not None

def test_models_import():
    from app.models import Base, User, Inspection
    assert Base is not None

def test_schemas_import():
    from app.schemas.ai_result import AIAnalyzeResponse
    from app.schemas.inspection import InspectionCreateResponse
    assert AIAnalyzeResponse is not None

def test_ai_client_import():
    from app.clients.ai_client import AIServiceClient
    assert AIServiceClient is not None

def test_mock_response_validation():
    from app.clients.ai_client import AIServiceClient
    from app.schemas.ai_result import AIAnalyzeResponse
    
    client = AIServiceClient(mock_mode=True)
    resp = client._generate_mock_response("test-123")
    assert isinstance(resp, AIAnalyzeResponse)
    assert resp.success is True
    assert resp.scan_id == "test-123"
