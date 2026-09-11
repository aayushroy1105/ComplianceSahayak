import urllib.request
import urllib.parse
import urllib.error
import json
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys

sys.path.insert(0, "/Users/aayushroy/SIH/SIH_BACKEND/backend")
from app.models.user import User
from app.core.security import verify_password, get_password_hash

BASE_URL = "http://127.0.0.1:8000/api/v1"

def login(email, password):
    data = urllib.parse.urlencode({"username": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()) if e.length else None

def get_me(token):
    req = urllib.request.Request(f"{BASE_URL}/users/me", method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()) if e.length else None

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
            if u.email == u_email:
                if not verify_password(u_pass, u.password_hash):
                    u.password_hash = get_password_hash(u_pass)
            elif u.email == o_email:
                if not verify_password(o_pass, u.password_hash):
                    u.password_hash = get_password_hash(o_pass)
        await db.commit()
        
    st_u, res_u = login(u_email, u_pass)
    st_o, res_o = login(o_email, o_pass)
    
    print(f"USER LOGIN: {'PASS' if st_u == 200 else 'FAIL'}")
    if st_u == 200:
        st_ume, res_ume = get_me(res_u["access_token"])
        print(f"USER /users/me: {'PASS' if st_ume == 200 else f'FAIL ({st_ume})'}")
        print(f"USER ROLE: {res_ume.get('role', 'OTHER') if st_ume == 200 else 'OTHER'}")
    
    print(f"OFFICER LOGIN: {'PASS' if st_o == 200 else 'FAIL'}")
    if st_o == 200:
        st_ome, res_ome = get_me(res_o["access_token"])
        print(f"OFFICER /users/me: {'PASS' if st_ome == 200 else f'FAIL ({st_ome})'}")
        print(f"OFFICER ROLE: {res_ome.get('role', 'OTHER') if st_ome == 200 else 'OTHER'}")

asyncio.run(main())
