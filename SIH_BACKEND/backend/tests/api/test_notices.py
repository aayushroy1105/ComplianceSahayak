import pytest
from httpx import AsyncClient
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notice import EnforcementNotice
from sqlalchemy import select

@pytest.mark.asyncio
async def test_issue_notice(client: AsyncClient, setup_test_users, db: AsyncSession):
    officer_token = setup_test_users["officer_token"]
    user_token = setup_test_users["user_token"]
    
    from app.models.inspection import Inspection
    import uuid
    inspection_id = str(uuid.uuid4())
    user_id = setup_test_users["user"].id
    inspection = Inspection(id=inspection_id, user_id=user_id, inspection_code="TEST-123")
    db.add(inspection)
    await db.commit()

    
    # User shouldn't be able to issue notice
    res = await client.post(
        f"{settings.API_V1_STR}/inspections/{inspection_id}/notice",
        json={"remarks": "Test notice"},
        cookies={"access_token": user_token}
    )
    assert res.status_code == 403

    # Officer issues notice
    res = await client.post(
        f"{settings.API_V1_STR}/inspections/{inspection_id}/notice",
        json={"remarks": "Test notice"},
        cookies={"access_token": officer_token}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["remarks"] == "Test notice"
    assert data["status"] == "ISSUED"
    
    # Retrieve notices
    res = await client.get(
        f"{settings.API_V1_STR}/inspections/{inspection_id}/notices",
        cookies={"access_token": user_token}
    )
    assert res.status_code == 200
    notices = res.json()
    assert len(notices) == 1
    assert notices[0]["remarks"] == "Test notice"
