import requests
import json
import sys

img_path = sys.argv[1]
with open(img_path, 'rb') as f:
    files = {'file': f}
    # Using the local paddle ocr api running on port 8002
    res = requests.post('http://127.0.0.1:8002/ocr/extract', files=files)
    data = res.json()
    for idx, block in enumerate(data.get('blocks', [])):
        print(f"Block {idx}: text='{block.get('text')}', conf={block.get('confidence'):.4f}, bbox={block.get('bbox')}")
