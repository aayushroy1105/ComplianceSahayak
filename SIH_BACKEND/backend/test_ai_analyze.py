import asyncio
from app.clients.ai_client import AIServiceClient

async def test_ai_analyze():
    client = AIServiceClient(mock_mode=False) 
    try:
        response = await client.analyze(
            image_bytes=b"fakeimagebytes",
            image_filename="test.jpg",
            image_mime_type="image/jpeg",
            scan_id="scan_12345"
        )
        print("Analyze Success!")
        print(response.model_dump_json(indent=2))
    except Exception as e:
        print(f"Analyze Failed: {e}")
        
asyncio.run(test_ai_analyze())
