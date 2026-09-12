import asyncio
import json
import httpx
import os

async def main():
    print("Fetching API from localhost:8000")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post("http://localhost:8000/api/v1/auth/login", data={"username": "officer@example.com", "password": "password123"})
            if res.status_code != 200:
                print("Login failed:", res.status_code, res.text)
                res = await client.post("http://localhost:8000/api/v1/auth/login", data={"username": "admin@example.com", "password": "password123"})
                if res.status_code != 200:
                    print("Admin login failed:", res.status_code, res.text)
                    return
            
            token = res.json()["access_token"]
            print("Got token")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Analytics uses getInspections with no scope?
            res = await client.get("http://localhost:8000/api/v1/inspections/?page=1&page_size=500", headers=headers)
            print("Analytics API response:", res.status_code)
            data = res.json()
            if isinstance(data, dict):
                print("Total items:", data.get("pagination", {}).get("total_items"))
                items = data.get("items", [])
                print("Item count:", len(items))
                for item in items[:3]:
                    print(f"ID: {item.get('id')}, Lat: {item.get('latitude')}, Lng: {item.get('longitude')}, Date: {item.get('inspection_date')}, Status: {item.get('compliance_status')}")
            else:
                print("Unexpected response:", str(data)[:200])
                
            print("\nComparing with Dashboard API response:")
            # Dashboard uses what? Let's check the dashboard code.
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
