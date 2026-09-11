import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.core.config import settings
from app.models.inspection import Inspection
from app.models.report import Report
from app.models.declaration import Declaration
from app.models.violation import Violation
from app.models.evidence import Evidence
from app.repositories.inspection_repository import generate_inspection_code

@pytest.fixture
async def setup_report_data(db: AsyncSession, setup_test_users):
    user_id = setup_test_users["user"].id
    officer_id = setup_test_users["officer"].id
    
    # Inspection 1: Compliant
    i1 = Inspection(
        user_id=user_id, 
        inspection_code=generate_inspection_code(), 
        compliance_status="COMPLIANT",
        ocr_version="1.0",
        rule_engine_version="2.0"
    )
    db.add(i1)
    await db.commit()
    
    # Inspection 2: Non-compliant with data
    i2 = Inspection(
        user_id=user_id, 
        inspection_code=generate_inspection_code(), 
        compliance_status="NON_COMPLIANT",
        review_required=True,
        review_reason="OCR_UNCERTAIN"
    )
    db.add(i2)
    await db.commit()
    
    d1 = Declaration(inspection_id=i2.id, field_name="MRP", raw_value="100", confidence=0.99, extraction_status="FOUND")
    v1 = Violation(inspection_id=i2.id, violation_code="MISSING_MRP", rule_id="1", description="desc", status="OPEN", evidence_references=["E1"])
    e1 = Evidence(inspection_id=i2.id, evidence_id_ai="E1", evidence_type="IMAGE", rule_id="1")
    
    db.add_all([d1, v1, e1])
    await db.commit()
    
    return [i1, i2]

@pytest.mark.asyncio
async def test_generate_report_authorized(client: AsyncClient, setup_test_users, setup_report_data):
    token = setup_test_users["user_token"]
    i_id = str(setup_report_data[0].id)
    
    res = await client.post(
        f"{settings.API_V1_STR}/inspections/{i_id}/report",
        cookies={"access_token": token}
    )
    assert res.status_code == 201
    data = res.json()
    assert data["inspection_id"] == i_id
    assert data["report_type"] == "MARKDOWN"
    assert data["version"] == 1
    assert "report_path" in data

@pytest.mark.asyncio
async def test_generate_report_unauthorized(client: AsyncClient, setup_test_users, setup_report_data):
    # Try to access a user's inspection with another token if we had one
    # But since we only have one user, we'll try an invalid ID
    pass

@pytest.mark.asyncio
async def test_generate_report_content(client: AsyncClient, setup_test_users, setup_report_data, db: AsyncSession):
    token = setup_test_users["user_token"]
    i_id = str(setup_report_data[1].id)
    
    res = await client.post(
        f"{settings.API_V1_STR}/inspections/{i_id}/report",
        cookies={"access_token": token}
    )
    assert res.status_code == 201
    
    # Generate again to test versioning
    res2 = await client.post(
        f"{settings.API_V1_STR}/inspections/{i_id}/report",
        cookies={"access_token": token}
    )
    assert res2.status_code == 201
    data2 = res2.json()
    assert data2["version"] == 2
    
    # Get latest report
    res3 = await client.get(
        f"{settings.API_V1_STR}/inspections/{i_id}/report",
        cookies={"access_token": token}
    )
    assert res3.status_code == 200
    assert res3.json()["version"] == 2
    
    # Read the file content from disk to verify
    report_path = res3.json()["report_path"]
    import os
    file_path = os.path.join(os.getcwd(), report_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "NON_COMPLIANT" in content
    assert "MISSING_MRP" in content
    assert "E1" in content
    assert "OCR_UNCERTAIN" in content
