import urllib.request
import urllib.parse
import json

BASE = 'http://localhost:8000/api/v1'

def post_form(url, form_data):
    body = urllib.parse.urlencode(form_data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def post_json(url, data, token=None):
    body = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', 'application/json')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

def post_multipart(url, fields, files, token=None):
    boundary = '----WebKitFormBoundaryE2ETest12345678'
    body = bytearray()
    for k, v in fields.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode('utf-8'))
        body.extend(f'{v}\r\n'.encode('utf-8'))
    for field_name, (filename, file_bytes, content_type) in files.items():
        body.extend(f'--{boundary}\r\n'.encode('utf-8'))
        body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"\r\n'.encode('utf-8'))
        body.extend(f'Content-Type: {content_type}\r\n\r\n'.encode('utf-8'))
        body.extend(file_bytes)
        body.extend(b'\r\n')
    body.extend(f'--{boundary}--\r\n'.encode('utf-8'))
    
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode('utf-8'))

print("Logging in user...")
status, user_data = post_form(f'{BASE}/auth/login', {'username': 'e2e.user@compliancesahayak.dev', 'password': 'Iyib4oXLfP1BTpxgYj0DO1Kv'})
user_token = user_data['access_token']

print("Creating inspection...")
status, inspection = post_json(f'{BASE}/inspections', {
    'product_name': 'Minimalist',
    'brand_name': 'Minimalist',
    'location_text': 'Mumbai'
}, token=user_token)
insp_id = inspection['id']

print("Uploading image...")
image_path = "/Users/aayushroy/SIH/SIH_BACKEND/backend/uploads/a87a459027b04c10bf4c5b1e48ba5b2eg"
with open(image_path, 'rb') as f:
    real_img = f.read()

status, img_record = post_multipart(
    f'{BASE}/inspections/{insp_id}/images',
    {'image_type': 'FRONT'},
    {'image': ('minimalist.jpg', real_img, 'image/jpeg')},
    token=user_token
)

print("Running AI analysis...")
status, analysis_res = post_json(f'{BASE}/inspections/{insp_id}/analyze', {}, token=user_token)
print("--- RAW OCR BLOCKS ---")
for idx, b in enumerate(analysis_res.get('raw_ocr_blocks', [])):
    print(f"Block {idx}: text='{b.get('text')}', conf={b.get('confidence')}, bbox={b.get('bbox')}")
