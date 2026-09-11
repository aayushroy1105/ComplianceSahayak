import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.core.config import settings
from app.models.inspection import Inspection
from app.repositories.inspection_repository import generate_inspection_code

@pytest.mark.asyncio
async def test_create_inspection_invalid_latitude(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        cookies={"access_token": token},
        json={"latitude": 91.0, "longitude": 10.0}
    )
    assert res.status_code == 422 # Pydantic Field validation catches this
    
@pytest.mark.asyncio
async def test_create_inspection_invalid_longitude(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        cookies={"access_token": token},
        json={"latitude": 10.0, "longitude": -181.0}
    )
    assert res.status_code == 422
    
@pytest.mark.asyncio
async def test_create_inspection_valid_coordinates(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        cookies={"access_token": token},
        json={"latitude": 45.0, "longitude": 90.0, "location_text": "Store front"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["latitude"] == 45.0
    assert data["longitude"] == 90.0
    assert data["location_text"] == "Store front"

@pytest.mark.asyncio
async def test_create_inspection_no_coordinates(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        cookies={"access_token": token},
        json={}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["latitude"] is None
    assert data["longitude"] is None

@pytest.fixture
async def setup_location_data(db: AsyncSession, setup_test_users):
    user_id = setup_test_users["user"].id
    officer_id = setup_test_users["officer"].id
    
    # 2 inspections with coordinates
    i1 = Inspection(user_id=user_id, inspection_code=generate_inspection_code(), latitude=10.0, longitude=20.0, compliance_status="COMPLIANT")
    i2 = Inspection(user_id=officer_id, inspection_code=generate_inspection_code(), latitude=30.0, longitude=40.0, compliance_status="NON_COMPLIANT")
    
    # 1 without coordinates
    i3 = Inspection(user_id=user_id, inspection_code=generate_inspection_code())
    
    db.add_all([i1, i2, i3])
    await db.commit()

@pytest.mark.asyncio
async def test_get_inspection_locations_authorization(client: AsyncClient, setup_test_users, setup_location_data):
    # USER role should only see their own locations
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/locations",
        cookies={"access_token": token}
    )
    assert res.status_code == 200
    data = res.json()
    # User owns i1 (has coords) and i3 (no coords). Only i1 is returned.
    assert len(data["items"]) >= 1
    assert data["items"][0]["latitude"] == 10.0
    
    # OFFICER role should see all locations
    token_officer = setup_test_users["officer_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/locations",
        cookies={"access_token": token_officer}
    )
    assert res.status_code == 200
    data_officer = res.json()
    # Sees i1 and i2 (both have coords)
    assert len(data_officer["items"]) >= 2

@pytest.mark.asyncio
async def test_get_inspection_locations_filtering(client: AsyncClient, setup_test_users, setup_location_data):
    token_officer = setup_test_users["officer_token"]
    # Filter by compliance_status
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/locations?compliance_status=NON_COMPLIANT",
        cookies={"access_token": token_officer}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) >= 1
    assert data["items"][0]["latitude"] == 30.0
