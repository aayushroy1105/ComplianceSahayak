import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.core.config import settings
from app.services.manufacturer_service import get_or_create_manufacturer
from app.models.inspection import Inspection
from app.models.violation import Violation
from app.repositories.inspection_repository import generate_inspection_code

@pytest.fixture
async def setup_analytics_data(db: AsyncSession, setup_test_users):
    user_id = setup_test_users["user"].id
    m1 = await get_or_create_manufacturer(db, "Offender Corp")
    m2 = await get_or_create_manufacturer(db, "Good Corp")
    
    # Offender Corp gets 2 inspections with the SAME violation code (Repeat offender!)
    # Plus one inspection with a different code
    insp1 = Inspection(user_id=user_id, manufacturer_id=m1.id, inspection_code=generate_inspection_code())
    insp2 = Inspection(user_id=user_id, manufacturer_id=m1.id, inspection_code=generate_inspection_code())
    insp3 = Inspection(user_id=user_id, manufacturer_id=m1.id, inspection_code=generate_inspection_code())
    
    # Good Corp gets 1 inspection with 1 violation
    insp4 = Inspection(user_id=user_id, manufacturer_id=m2.id, inspection_code=generate_inspection_code())
    
    db.add_all([insp1, insp2, insp3, insp4])
    await db.commit()
    
    # Violations
    # Offender Corp repeat violation
    v1 = Violation(inspection_id=insp1.id, violation_code="MISSING_MRP", rule_id="rule1", description="desc", status="OPEN")
    v2 = Violation(inspection_id=insp2.id, violation_code="MISSING_MRP", rule_id="rule1", description="desc", status="OPEN")
    # Offender Corp multiple evidences same violation in same inspection -> counts as 1 violation inherently because it's 1 row in DB with array of evidence references, but let's test if we add 2 rows of same code it counts properly if grouped by inspection_id
    v3 = Violation(inspection_id=insp3.id, violation_code="MISSING_PKD", rule_id="rule2", description="desc", status="OPEN")
    
    # Good Corp single violation
    v4 = Violation(inspection_id=insp4.id, violation_code="MISSING_WEIGHT", rule_id="rule3", description="desc", status="OPEN")
    
    db.add_all([v1, v2, v3, v4])
    await db.commit()
    return m1, m2

@pytest.mark.asyncio
async def test_repeat_offenders_analytics_authorization(client: AsyncClient, setup_test_users):
    # USER role should be forbidden
    token = setup_test_users["user_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/analytics/repeat-offenders",
        cookies={"access_token": token}
    )
    assert res.status_code == 403
    
    # OFFICER role should succeed
    token_officer = setup_test_users["officer_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/analytics/repeat-offenders",
        cookies={"access_token": token_officer}
    )
    assert res.status_code == 200

@pytest.mark.asyncio
async def test_repeat_offenders_analytics_data(client: AsyncClient, setup_test_users, setup_analytics_data):
    token_officer = setup_test_users["officer_token"]
    res = await client.get(
        f"{settings.API_V1_STR}/analytics/repeat-offenders",
        cookies={"access_token": token_officer}
    )
    assert res.status_code == 200
    data = res.json()
    offenders = data["offenders"]
    
    assert len(offenders) >= 2
    
    offender_corp = next((o for o in offenders if o["manufacturer_name"] == "Offender Corp"), None)
    assert offender_corp is not None
    assert offender_corp["total_inspections"] == 3
    assert offender_corp["total_violations"] == 3
    assert offender_corp["repeat_violation_count"] == 1 # MISSING_MRP repeated across 2 inspections
    assert "MISSING_MRP" in offender_corp["top_violation_codes"]
    
    good_corp = next((o for o in offenders if o["manufacturer_name"] == "Good Corp"), None)
    assert good_corp is not None
    assert good_corp["total_inspections"] == 1
    assert good_corp["total_violations"] == 1
    assert good_corp["repeat_violation_count"] == 0 # no repeat violations
