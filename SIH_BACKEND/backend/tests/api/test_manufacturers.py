import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.core.config import settings
from app.services.manufacturer_service import get_or_create_manufacturer, normalize_manufacturer_name

@pytest.mark.asyncio
async def test_normalization_logic():
    assert normalize_manufacturer_name("ABC Foods, Inc.") == "abc foods inc"
    assert normalize_manufacturer_name("  DEF   Corp! ") == "def corp"
    assert normalize_manufacturer_name("XYZ-123") == "xyz 123"

@pytest.fixture
async def sample_manufacturers(db: AsyncSession):
    m1 = await get_or_create_manufacturer(db, "Test Manufacturer A")
    m2 = await get_or_create_manufacturer(db, "Test Manufacturer B")
    m3 = await get_or_create_manufacturer(db, "Test Manufacturer C")
    return [m1, m2, m3]

@pytest.mark.asyncio
async def test_list_manufacturers(client: AsyncClient, setup_test_users, sample_manufacturers):
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/manufacturers",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) >= 3
    assert data["pagination"]["total_items"] >= 3

@pytest.mark.asyncio
async def test_search_manufacturers(client: AsyncClient, setup_test_users, sample_manufacturers):
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/manufacturers?search=manufacturer a",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Manufacturer A"

@pytest.mark.asyncio
async def test_get_manufacturer_detail(client: AsyncClient, setup_test_users, sample_manufacturers):
    token = setup_test_users["user_token"]
    m_id = str(sample_manufacturers[0].id)
    res = await client.get(
        f"{settings.API_V1_STR}/manufacturers/{m_id}",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == m_id
    assert "products" in data

@pytest.mark.asyncio
async def test_get_manufacturer_history(client: AsyncClient, setup_test_users, sample_manufacturers, db: AsyncSession):
    # First create an inspection for this manufacturer
    token = setup_test_users["user_token"]
    m = sample_manufacturers[0]
    
    from app.models.inspection import Inspection
    from app.repositories.inspection_repository import generate_inspection_code
    insp = Inspection(
        user_id=setup_test_users["user"].id,
        manufacturer_id=m.id,
        inspection_code=generate_inspection_code(),
        processing_status="COMPLETED",
        compliance_status="COMPLIANT"
    )
    db.add(insp)
    await db.commit()
    await db.refresh(insp)
    
    res = await client.get(
        f"{settings.API_V1_STR}/manufacturers/{m.id}/history",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(insp.id)
    assert data["items"][0]["violation_count"] == 0
