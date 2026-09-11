import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import get_password_hash, create_access_token
from app.core.config import settings

@pytest.fixture
async def setup_users(db: AsyncSession):
    user = User(
        name="Test User",
        email="user@example.com",
        password_hash=get_password_hash("password123"),
        role="USER",
        is_active=True
    )
    officer = User(
        name="Test Officer",
        email="officer@example.com",
        password_hash=get_password_hash("password123"),
        role="OFFICER",
        is_active=True
    )
    admin = User(
        name="Test Admin",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role="ADMIN",
        is_active=True
    )
    db.add_all([user, officer, admin])
    await db.commit()
    return user, officer, admin

@pytest.mark.asyncio
async def test_1_valid_user_credentials(client: AsyncClient, setup_users):
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "cookie"
    assert "password_hash" not in data.get("user", {}) # test 13

@pytest.mark.asyncio
async def test_2_invalid_password(client: AsyncClient, setup_users):
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_3_nonexistent_user(client: AsyncClient, setup_users):
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nonexistent@example.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

@pytest.mark.asyncio
async def test_4_successful_token_issuance(client: AsyncClient, setup_users):
    response = await client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "officer@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_5_valid_token_authentication(client: AsyncClient, setup_users):
    token = create_access_token("user@example.com")
    response = await client.get(
        f"{settings.API_V1_STR}/users/me",
        cookies={"access_token": token}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@example.com"
    assert "password_hash" not in data # test 13

@pytest.mark.asyncio
async def test_6_invalid_token(client: AsyncClient, setup_users):
    response = await client.get(
        f"{settings.API_V1_STR}/users/me",
        cookies={"access_token": "invalidtoken"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_7_expired_token(client: AsyncClient, setup_users):
    from datetime import timedelta
    token = create_access_token("user@example.com", expires_delta=timedelta(minutes=-1))
    response = await client.get(
        f"{settings.API_V1_STR}/users/me",
        cookies={"access_token": token}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_8_missing_token(client: AsyncClient, setup_users):
    response = await client.get(f"{settings.API_V1_STR}/users/me")
    assert response.status_code == 401

# For testing authorization, we need mock routes that use the role dependencies
from fastapi import APIRouter, Depends
from app.api.dependencies import require_user, require_officer, require_admin
from app.main import app

test_router = APIRouter()

@test_router.get("/test-user")
def user_route(user=Depends(require_user)): return {"status": "ok"}

@test_router.get("/test-officer")
def officer_route(user=Depends(require_officer)): return {"status": "ok"}

@test_router.get("/test-admin")
def admin_route(user=Depends(require_admin)): return {"status": "ok"}

app.include_router(test_router, prefix="/test")

@pytest.mark.asyncio
async def test_9_user_authorization(client: AsyncClient, setup_users):
    token = create_access_token("user@example.com")
    # User can access require_user
    res = await client.get("/test/test-user", cookies={"access_token": token})
    assert res.status_code == 200
    # User cannot access require_officer or require_admin
    res2 = await client.get("/test/test-officer", cookies={"access_token": token})
    assert res2.status_code == 403
    res3 = await client.get("/test/test-admin", cookies={"access_token": token})
    assert res3.status_code == 403

@pytest.mark.asyncio
async def test_10_officer_authorization(client: AsyncClient, setup_users):
    token = create_access_token("officer@example.com")
    # Officer can access require_user and require_officer
    assert (await client.get("/test/test-user", cookies={"access_token": token})).status_code == 200
    assert (await client.get("/test/test-officer", cookies={"access_token": token})).status_code == 200
    # Officer cannot access require_admin
    assert (await client.get("/test/test-admin", cookies={"access_token": token})).status_code == 403

@pytest.mark.asyncio
async def test_11_admin_authorization(client: AsyncClient, setup_users):
    token = create_access_token("admin@example.com")
    # Admin can access all
    assert (await client.get("/test/test-user", cookies={"access_token": token})).status_code == 200
    assert (await client.get("/test/test-officer", cookies={"access_token": token})).status_code == 200
    assert (await client.get("/test/test-admin", cookies={"access_token": token})).status_code == 200

@pytest.mark.asyncio
async def test_12_role_escalation_attempt(client: AsyncClient, setup_users):
    token = create_access_token("user@example.com")
    response = await client.get("/test/test-admin", cookies={"access_token": token})
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"

@pytest.mark.asyncio
async def test_14_jwt_secret_not_hardcoded():
    # Verify the secret key is not any of the known insecure defaults
    insecure_defaults = {
        "hardcoded",
        "a-very-secret-key-change-in-production",
        "your-super-secret-key-for-jwt-do-not-use-in-production",
    }
    assert settings.SECRET_KEY not in insecure_defaults, (
        f"SECRET_KEY must not be an insecure default placeholder"
    )
    assert len(settings.SECRET_KEY) >= 32, "SECRET_KEY must be at least 32 characters"

