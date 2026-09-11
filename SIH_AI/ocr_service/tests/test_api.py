import io
from fastapi.testclient import TestClient
from app.main import app
from PIL import Image, ImageDraw, ImageFont

client = TestClient(app)

def create_synthetic_image_bytes():
    # Create a simple white image with black text
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    # Draw some text
    d.text((50, 80), "MRP 150.00", fill=(0, 0, 0))
    d.text((50, 120), "MFG 01/2026", fill=(0, 0, 0))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "ocr_engine"
    assert "model_initialized" in data

def test_extract_success():
    payload = {"scan_id": "TEST-123"}
    img_bytes = create_synthetic_image_bytes()
    files = {"image": ("dummy.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    
    response = client.post("/extract", data=payload, files=files)
    assert response.status_code == 200
    data = response.json()
    
    if not data["success"]:
        print(f"FAILED OCR RESPONSE: {data}")
        
    assert data["success"] is True
    assert data["image_id"] == "TEST-123"
    assert data["mock"] is False
    assert data["processing_time_ms"] > 0
    assert "paddleocr" in data["ocr_model_version"]
    
    # We generated real text, PaddleOCR should find it.
    blocks = data["text_blocks"]
    assert len(blocks) > 0
    
    # Validate bbox format
    for block in blocks:
        assert "text" in block
        assert "confidence" in block
        assert len(block["bbox"]) == 4 # [x_min, y_min, x_max, y_max]

def test_extract_missing_image():
    payload = {"scan_id": "TEST-123"}
    response = client.post("/extract", data=payload)
    assert response.status_code == 422  # FastAPI validation error

def test_extract_missing_scan_id():
    img_bytes = create_synthetic_image_bytes()
    files = {"image": ("dummy.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    response = client.post("/extract", files=files)
    assert response.status_code == 400
    assert "scan_id or request_id" in response.json()["detail"]
