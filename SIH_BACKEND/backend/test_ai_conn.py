import asyncio
from app.clients.ai_client import AIServiceClient

async def test_ai():
    client = AIServiceClient(mock_mode=False) # Important: override mock_mode because config defaults to True
    is_healthy = await client.health_check()
    print(f"AI Health Check Result: {is_healthy}")
    
asyncio.run(test_ai())
