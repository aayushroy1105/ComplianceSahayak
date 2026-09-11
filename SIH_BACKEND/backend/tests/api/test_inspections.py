import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User
from app.models.officer import Officer
from app.models.inspection import Inspection
from app.models.audit_log import AuditLog
import uuid
from datetime import datetime

@pytest.mark.asyncio
async def test_1_authenticated_user_creates_inspection(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        cookies={"access_token": token},
        json={"latitude": 19.0, "longitude": 72.0, "location_text": "Mumbai"}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["inspection_code"].startswith("INS-")
    assert data["processing_status"] == "PENDING"
    assert data["latitude"] == 19.0

@pytest.mark.asyncio
async def test_2_authenticated_officer_creates_inspection(client: AsyncClient, setup_test_users):
    token = setup_test_users["officer_token"]
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        cookies={"access_token": token},
        json={"latitude": 20.0, "longitude": 73.0, "officer_notes": "test notes"}
    )
    assert res.status_code == 201
    assert res.json()["processing_status"] == "PENDING"

@pytest.mark.asyncio
async def test_3_unauthorized_request_fails(client: AsyncClient):
    res = await client.post(
        f"{settings.API_V1_STR}/inspections",
        json={"latitude": 19.0, "longitude": 72.0}
    )
    assert res.status_code == 401

@pytest.mark.asyncio
async def test_4_unique_inspection_code(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res1 = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    res2 = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    assert res1.json()["inspection_code"] != res2.json()["inspection_code"]

@pytest.mark.asyncio
async def test_6_inspection_persisted(client: AsyncClient, setup_test_users, db: AsyncSession):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    ins_id = res.json()["id"]
    
    # Check DB directly
    result = await db.execute(select(Inspection).where(Inspection.id == ins_id))
    ins = result.scalars().first()
    assert ins is not None

@pytest.mark.asyncio
async def test_7_user_relationship_persisted(client: AsyncClient, setup_test_users, db: AsyncSession):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    ins_id = res.json()["id"]
    result = await db.execute(select(Inspection).where(Inspection.id == ins_id))
    ins = result.scalars().first()
    assert ins.user_id == setup_test_users["user"].id
    assert ins.officer_id is None

@pytest.mark.asyncio
async def test_8_officer_relationship_persisted_when_applicable(client: AsyncClient, setup_test_users, db: AsyncSession):
    token = setup_test_users["officer_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    ins_id = res.json()["id"]
    result = await db.execute(select(Inspection).where(Inspection.id == ins_id))
    ins = result.scalars().first()
    assert ins.user_id == setup_test_users["officer"].id
    assert ins.officer_id == setup_test_users["officer_profile"].id

@pytest.mark.asyncio
async def test_11_valid_latitude(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={"latitude": 90.0})
    assert res.status_code == 201

@pytest.mark.asyncio
async def test_12_invalid_latitude(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={"latitude": 91.0})
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_13_valid_longitude(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={"longitude": 180.0})
    assert res.status_code == 201

@pytest.mark.asyncio
async def test_14_invalid_longitude(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={"longitude": 181.0})
    assert res.status_code == 422

@pytest.mark.asyncio
async def test_16_audit_log_created(client: AsyncClient, setup_test_users, db: AsyncSession):
    token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    ins_id = res.json()["id"]
    result = await db.execute(select(AuditLog).where(AuditLog.inspection_id == ins_id, AuditLog.action == "INSPECTION_CREATED"))
    audit = result.scalars().first()
    assert audit is not None
    assert audit.user_id == setup_test_users["user"].id

@pytest.mark.asyncio
async def test_17_user_cannot_access_unauthorized_inspection(client: AsyncClient, setup_test_users):
    # Officer creates one
    officer_token = setup_test_users["officer_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": officer_token}, json={})
    ins_id = res.json()["id"]
    
    # User tries to access it
    user_token = setup_test_users["user_token"]
    res2 = await client.get(f"{settings.API_V1_STR}/inspections/{ins_id}", cookies={"access_token": user_token})
    assert res2.status_code == 403

@pytest.mark.asyncio
async def test_18_officer_can_access_permitted_inspection(client: AsyncClient, setup_test_users):
    # User creates one
    user_token = setup_test_users["user_token"]
    res = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": user_token}, json={})
    ins_id = res.json()["id"]
    
    # Officer accesses it
    officer_token = setup_test_users["officer_token"]
    res2 = await client.get(f"{settings.API_V1_STR}/inspections/{ins_id}", cookies={"access_token": officer_token})
    assert res2.status_code == 200

@pytest.mark.asyncio
async def test_19_inspection_detail_retrieval(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    res1 = await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={"latitude": 10.0})
    ins_id = res1.json()["id"]
    
    res2 = await client.get(f"{settings.API_V1_STR}/inspections/{ins_id}", cookies={"access_token": token})
    assert res2.status_code == 200
    assert res2.json()["latitude"] == 10.0
    assert "inspection_code" in res2.json()

@pytest.mark.asyncio
async def test_20_inspection_list(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
    
    res = await client.get(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token})
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 2

@pytest.mark.asyncio
async def test_21_pagination(client: AsyncClient, setup_test_users):
    token = setup_test_users["user_token"]
    for _ in range(5):
        await client.post(f"{settings.API_V1_STR}/inspections", cookies={"access_token": token}, json={})
        
    res = await client.get(f"{settings.API_V1_STR}/inspections?page=1&page_size=2", cookies={"access_token": token})
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["page_size"] == 2
    assert data["pagination"]["total_items"] >= 5
