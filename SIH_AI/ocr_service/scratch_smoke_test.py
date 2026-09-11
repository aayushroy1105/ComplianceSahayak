import io
import time
from PIL import Image, ImageDraw, ImageFont
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Ensure model is initialized
print("Initializing OCR Engine via lifespan...")
client.get("/health") 

TEST_CASES = [
    {"name": "Manufacturer", "text": "Manufactured by: ABC Foods Pvt Ltd"},
    {"name": "Packer", "text": "Packed by: XYZ Packaging, Mumbai"},
    {"name": "Importer", "text": "Imported by: Global Traders Inc."},
    {"name": "Product Name", "text": "Super Premium Darjeeling Tea"},
    {"name": "MRP", "text": "MRP Rs.120.00 (Incl. of all taxes)"},
    {"name": "Net Quantity", "text": "Net Quantity: 500 g"},
    {"name": "Manufacturing Date", "text": "Mfg. Date: 05/09/2026"},
    {"name": "Country of Origin", "text": "Country of Origin: India"},
    {"name": "Consumer Care", "text": "Consumer Care: 1800-111-2222"},
    {
        "name": "Multiple Fields", 
        "text": "MRP ₹150\nNet Qty: 1 kg\nMfg Date: 12/2025"
    }
]

def create_image_bytes(text: str) -> bytes:
    img = Image.new('RGB', (600, 300), color='white')
    d = ImageDraw.Draw(img)
    
    # We draw text line by line if there are newlines
    lines = text.split('\n')
    y_text = 50
    for line in lines:
        d.text((50, y_text), line, fill=(0, 0, 0))
        y_text += 40
        
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

print("\n" + "="*60)
print("REAL OCR SMOKE TEST")
print("="*60)

for idx, tc in enumerate(TEST_CASES):
    print(f"\n--- Test {idx+1}: {tc['name']} ---")
    img_bytes = create_image_bytes(tc['text'])
    
    start_time = time.time()
    response = client.post(
        "/extract", 
        data={"scan_id": f"TEST-{idx+1}"}, 
        files={"image": ("test.jpg", io.BytesIO(img_bytes), "image/jpeg")}
    )
    req_time = (time.time() - start_time) * 1000
    
    assert response.status_code == 200
    data = response.json()
    
    print(f"INPUT TEXT: {repr(tc['text'])}")
    
    if not data['success']:
        print(f"ERROR: {data.get('error_message')}")
        continue
        
    print(f"PROCESSING TIME (Total API): {req_time:.2f} ms")
    print(f"OCR ENGINE TIME: {data['processing_time_ms']} ms")
    
    for i, block in enumerate(data['text_blocks']):
        print(f"  BLOCK {i+1}:")
        print(f"    DETECTED TEXT: {repr(block['text'])}")
        print(f"    CONFIDENCE: {block['confidence']:.4f}")
        print(f"    BOUNDING BOX: {block['bbox']}")

print("\nSmoke tests completed successfully.")
