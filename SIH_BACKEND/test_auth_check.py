import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys

sys.path.insert(0, "/Users/aayushroy/SIH/SIH_BACKEND/backend")
from app.models.user import User
from app.core.security import verify_password, get_password_hash

async def main():
    engine = create_async_engine("postgresql+asyncpg://postgres:raghav@localhost:5432/sih_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    u_email = "e2e.user@compliancesahayak.dev"
    o_email = "e2e.officer@compliancesahayak.dev"
    u_pass = "PJq2pX3xDmbrKiM8c1fvaR4V"
    o_pass = "OG7Xdyn1I_b7F_g1tUrZPc3eoIvtV01q"
    
    async with async_session() as db:
        res = await db.execute(select(User).where(User.email.in_([u_email, o_email])))
        users = res.scalars().all()
        for u in users:
            print(f"User: {u.email}, Active: {u.is_active}, Role: {u.role}")
            if u.email == u_email:
                print("User Password Match:", verify_password(u_pass, u.hashed_password))
                if not verify_password(u_pass, u.hashed_password):
                    u.hashed_password = get_password_hash(u_pass)
            elif u.email == o_email:
                print("Officer Password Match:", verify_password(o_pass, u.hashed_password))
                if not verify_password(o_pass, u.hashed_password):
                    u.hashed_password = get_password_hash(o_pass)
        await db.commit()

asyncio.run(main())
