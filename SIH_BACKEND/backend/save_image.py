import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import base64

engine = create_async_engine("postgresql+asyncpg://postgres:raghav@localhost:5432/sih_db")

async def main():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT id, image_data FROM inspection_images ORDER BY created_at DESC LIMIT 1;"))
        row = result.fetchone()
        if not row:
            print("No image found")
            return
            
        img_data_b64 = row[1]
        img_bytes = base64.b64decode(img_data_b64.split(",")[-1] if "," in img_data_b64 else img_data_b64)
        with open("/Users/aayushroy/SIH/SIH_AI/ai/min_test.jpg", "wb") as f:
            f.write(img_bytes)
        print("Image saved")

if __name__ == "__main__":
    asyncio.run(main())
