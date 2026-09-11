import requests

# Assuming backend is running on 8000
res = requests.post("http://localhost:8000/api/v1/auth/login", data={"username":"e2e.user@compliancesahayak.dev", "password":"E2eUserPass!123"})
if res.status_code == 200:
    token = res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("http://localhost:8000/api/v1/inspections?start_date=2026-08-13T00:00:00.000Z", headers=headers)
    print(r.status_code)
    try:
        print(len(r.json().get("items", [])))
    except:
        print(r.json())
else:
    print("Login failed", res.json())
