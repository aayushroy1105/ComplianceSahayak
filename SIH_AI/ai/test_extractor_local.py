import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.extraction.extractor import DeclarationExtractor

# Minimalist blocks as specified
blocks = [
    {"text": "Uprising Science Pvt. Ltd.", "confidence": 0.98, "bbox": [0,10,10,20]},
    {"text": "30 ml / 1.01 fl. oz.", "confidence": 0.95, "bbox": [0,30,10,40]},
    {"text": "MRP / Unit Sale Price / Batch No. / Mfg. Date / Exp. Date", "confidence": 0.95, "bbox": [0,60,10,70]},
    {"text": "Rs. 499  01/2026  01/2028", "confidence": 0.94, "bbox": [0,71,10,81]},
    {"text": "Country of Origin: India", "confidence": 0.9, "bbox": [0,90,10,100]},
    {"text": "For Consumer Complaints / Queries", "confidence": 0.9, "bbox": [0,110,10,120]}
]

extractor = DeclarationExtractor()
decls = extractor.extract(blocks, image_id="img1")

for d in decls:
    print(f"{d.field_name}: status={d.extraction_status}, raw={repr(d.raw_value)}, norm={repr(d.normalized_value)}")
