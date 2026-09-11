import urllib.request
import urllib.parse
import urllib.error
import json
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1"

def login(email, password):
    data = urllib.parse.urlencode({"username": email, "password": password}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode()) if e.length else None

print(login("e2e.user@compliancesahayak.dev", "PJq2pX3xDmbrKiM8c1fvaR4V"))
print(login("e2e.officer@compliancesahayak.dev", "OG7Xdyn1I_b7F_g1tUrZPc3eoIvtV01q"))
