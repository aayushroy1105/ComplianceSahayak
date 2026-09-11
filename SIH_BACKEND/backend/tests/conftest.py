import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.config import settings
from app.db.session import get_db
import uuid
from app.models.user import User
from app.models.officer import Officer
from app.core.security import get_password_hash, create_access_token

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)
    TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.begin_nested()
        async_session = TestingSessionLocal(bind=conn)
        yield async_session
        await async_session.close()
        await conn.rollback()
        
    await engine.dispose()

@pytest.fixture(scope="function")
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        c.cookies.set("csrf_token", "test_csrf_token")
        c.headers.update({"x-csrf-token": "test_csrf_token"})
        yield c
        
    app.dependency_overrides.clear()

@pytest.fixture
async def setup_test_users(db: AsyncSession):
    user_id = uuid.uuid4()
    officer_id = uuid.uuid4()
    officer_profile_id = uuid.uuid4()
    
    user = User(id=user_id, name="Test User", email="user@example.com", password_hash=get_password_hash("test"), role="USER", is_active=True)
    officer_user = User(id=officer_id, name="Test Officer", email="officer@example.com", password_hash=get_password_hash("test"), role="OFFICER", is_active=True)
    
    db.add_all([user, officer_user])
    await db.commit()
    await db.refresh(officer_user)
    
    officer_profile = Officer(id=officer_profile_id, user_id=officer_user.id, badge_number="BADGE001")
    db.add(officer_profile)
    await db.commit()
    
    return {
        "user": user,
        "officer": officer_user,
        "officer_profile": officer_profile,
        "user_token": create_access_token(user.email),
        "officer_token": create_access_token(officer_user.email)
    }
