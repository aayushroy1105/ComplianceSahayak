import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.config import settings

@pytest.fixture
async def sample_inspection_with_data(client: AsyncClient, setup_test_users, db: AsyncSession):
    token = setup_test_users["user_token"]
    # 1. Create inspection
    res = await client.post(
        f"{settings.API_V1_STR}/inspections", 
        cookies={"access_token": token}, 
        json={"latitude": 10.0, "longitude": 10.0}
    )
    inspection_id = res.json()["id"]
    
    # 2. Upload image (need to mock AI analysis, so we just directly hit analyze after uploading image)
    import io
    from PIL import Image
    
    img = Image.new('RGB', (10, 10), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_bytes = img_byte_arr.getvalue()
    
    files = {'image': ('test.jpg', image_bytes, 'image/jpeg')}
    data = {'image_type': 'FRONT'}
    await client.post(
        f"{settings.API_V1_STR}/inspections/{inspection_id}/images",
        cookies={"access_token": token},
        data=data,
        files=files
    )
    
    # 3. Analyze it to populate violations and evidence
    from unittest.mock import patch, AsyncMock
    from app.clients.ai_client import AIServiceClient
    mock_ai_client = AIServiceClient(mock_mode=True)
    mock_response = mock_ai_client._generate_mock_response("test")
    
    with patch("app.api.routes.inspections.ai_client_instance", mock_ai_client):
        with patch.object(mock_ai_client, 'analyze', new_callable=AsyncMock, return_value=mock_response):
            await client.post(
                f"{settings.API_V1_STR}/inspections/{inspection_id}/analyze",
                cookies={"access_token": token}
            )
            
    return inspection_id


@pytest.mark.asyncio
async def test_get_inspection_full_result(client: AsyncClient, setup_test_users, sample_inspection_with_data):
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/{sample_inspection_with_data}",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == sample_inspection_with_data
    assert "violations" in data
    assert "evidence" in data
    assert "declarations" in data
    assert len(data["violations"]) > 0
    assert len(data["evidence"]) > 0
    assert len(data["declarations"]) > 0

@pytest.mark.asyncio
async def test_get_inspection_violations(client: AsyncClient, setup_test_users, sample_inspection_with_data):
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/{sample_inspection_with_data}/violations",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "violation_code" in data[0]

@pytest.mark.asyncio
async def test_get_inspection_evidence(client: AsyncClient, setup_test_users, sample_inspection_with_data):
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/{sample_inspection_with_data}/evidence",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "evidence_type" in data[0]
