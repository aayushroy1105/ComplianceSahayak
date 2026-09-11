import requests

url = "http://localhost:8002/ai/analyze"
files = {"image": ("1310003997_Back.jpeg", open("../1310003997_Back.jpeg", "rb"), "image/jpeg")}
data = {"scan_id": "TEST-123"}
print("Sending request to AI...")
resp = requests.post(url, files=files, data=data)
print(resp.status_code)
print(resp.text)
