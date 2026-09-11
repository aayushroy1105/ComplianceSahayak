import os
import io
import pytest
import respx
import httpx
from unittest.mock import patch
from clients.ocr_client import OCRClient
from api.errors import AIAPIException
from PIL import Image, ImageDraw

@pytest.fixture
def ocr_client():
    return OCRClient()

@pytest.fixture
def dummy_image(tmp_path):
    img_path = tmp_path / "dummy.jpg"
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    d.text((50, 80), "MRP 150.00", fill=(0, 0, 0))
    img.save(img_path, format='JPEG')
    return str(img_path)

@respx.mock
@pytest.mark.asyncio
async def test_ocr_client_success(ocr_client, dummy_image):
    respx.post("http://localhost:8001/extract").mock(return_value=httpx.Response(
        200, json={
            "success": True,
            "image_id": "TEST-1",
            "text_blocks": [{"text": "MRP 150.00", "confidence": 0.99, "bbox": [50, 80, 150, 100]}],
            "ocr_model_version": "paddleocr_v2.6+",
            "processing_time_ms": 100,
            "mock": False
        }
    ))
    
    result = await ocr_client.extract_text(dummy_image, "TEST-1")
    assert result["success"] is True
    assert result["image_id"] == "TEST-1"

@respx.mock
@pytest.mark.asyncio
async def test_ocr_client_unavailable(ocr_client, dummy_image):
    respx.post("http://localhost:8001/extract").mock(side_effect=httpx.ConnectError("Connection refused"))
    
    with pytest.raises(AIAPIException) as exc:
        await ocr_client.extract_text(dummy_image, "TEST-1")
    assert exc.value.category == "OCR_FAILURE"
    assert "Failed to connect" in exc.value.detail

@respx.mock
@pytest.mark.asyncio
async def test_ocr_client_timeout(ocr_client, dummy_image):
    respx.post("http://localhost:8001/extract").mock(side_effect=httpx.TimeoutException("Timeout"))
    
    with pytest.raises(AIAPIException) as exc:
        await ocr_client.extract_text(dummy_image, "TEST-1")
    assert exc.value.category == "OCR_FAILURE"
    assert "timed out" in exc.value.detail

@respx.mock
@pytest.mark.asyncio
async def test_ocr_client_http_error(ocr_client, dummy_image):
    respx.post("http://localhost:8001/extract").mock(return_value=httpx.Response(500))
    
    with pytest.raises(AIAPIException) as exc:
        await ocr_client.extract_text(dummy_image, "TEST-1")
    assert exc.value.category == "OCR_FAILURE"
    assert "HTTP error: 500" in exc.value.detail

@respx.mock
@pytest.mark.asyncio
async def test_ocr_client_malformed_json(ocr_client, dummy_image):
    respx.post("http://localhost:8001/extract").mock(return_value=httpx.Response(200, text="not json"))
    
    with pytest.raises(AIAPIException) as exc:
        await ocr_client.extract_text(dummy_image, "TEST-1")
    assert exc.value.category == "OCR_FAILURE"
    assert "Unexpected OCR communication error" in exc.value.detail
