import asyncio
import os
import secrets
import string
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys

sys.path.insert(0, "/Users/aayushroy/SIH/SIH_BACKEND/backend")
from app.models.user import User
from app.core.security import get_password_hash

def gen_pass():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(24))

async def main():
    u_email = "e2e.user@compliancesahayak.dev"
    o_email = "e2e.officer@compliancesahayak.dev"
    
    new_u_pass = gen_pass()
    new_o_pass = gen_pass()
    
    engine = create_async_engine("postgresql+asyncpg://postgres:raghav@localhost:5432/sih_db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        res = await db.execute(select(User).where(User.email.in_([u_email, o_email])))
        users = res.scalars().all()
        for u in users:
            if u.email == u_email:
                u.password_hash = get_password_hash(new_u_pass)
            elif u.email == o_email:
                u.password_hash = get_password_hash(new_o_pass)
        await db.commit()
        
    with open("/Users/aayushroy/SIH/SIH_BACKEND/E2E_LOCAL_CREDENTIALS.txt", "w") as f:
        f.write(f"--- OFFICER ACCOUNT ---\n")
        f.write(f"ROLE=OFFICER\n")
        f.write(f"USERNAME={o_email}\n")
        f.write(f"PASSWORD={new_o_pass}\n\n")
        f.write(f"--- USER ACCOUNT ---\n")
        f.write(f"ROLE=USER\n")
        f.write(f"USERNAME={u_email}\n")
        f.write(f"PASSWORD={new_u_pass}\n\n")

    print(f"Rotated to:\nUSER: {new_u_pass}\nOFFICER: {new_o_pass}")

asyncio.run(main())
