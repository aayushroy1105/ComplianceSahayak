import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import base64
import os
from paddleocr import PaddleOCR

engine = create_async_engine("postgresql+asyncpg://postgres:raghav@localhost:5432/sih_db")

async def main():
    async with engine.connect() as conn:
        # Assuming Minimalist is the most recent inspection
        result = await conn.execute(text("SELECT id, image_data FROM inspection_images ORDER BY created_at DESC LIMIT 1;"))
        row = result.fetchone()
        if not row:
            print("No image found")
            return
            
        img_id = row[0]
        img_data_b64 = row[1]
        
        # Save image to temp file
        img_bytes = base64.b64decode(img_data_b64.split(",")[-1] if "," in img_data_b64 else img_data_b64)
        img_path = f"min_test_{img_id}.jpg"
        with open(img_path, "wb") as f:
            f.write(img_bytes)
            
        # Run PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        result = ocr.ocr(img_path, cls=True)
        
        print("--- OCR BLOCKS ---")
        for idx, line in enumerate(result[0]):
            bbox = line[0]
            text_val = line[1][0]
            conf = line[1][1]
            print(f"Block {idx}: text='{text_val}', conf={conf:.4f}, bbox={bbox}")
            
if __name__ == "__main__":
    asyncio.run(main())
