import pytest
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base

# We are testing if metadata is complete and can generate tables
# NOTE: This test might fail if PostgreSQL is not available locally without a password.
@pytest.mark.asyncio
async def test_metadata_tables():
    assert "users" in Base.metadata.tables
    assert "inspections" in Base.metadata.tables
    assert "evidence" in Base.metadata.tables
    assert "violations" in Base.metadata.tables
    assert "enforcement_notices" in Base.metadata.tables
    assert len(Base.metadata.tables) == 15
