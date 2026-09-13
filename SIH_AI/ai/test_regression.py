from services.extraction.extractor import DeclarationExtractor

extractor = DeclarationExtractor()

# Test 1: CIPLA (Regression)
print("=== CIPLA ===")
blocks_cipla = [
    {"text": "Manufactured by Medispray Laboratories Pvt Ltd.", "confidence": 0.99, "bbox": [0,0,10,10]},
    {"text": "Amoxycillin Trihydrate Capsules IP 500 mg", "confidence": 0.98, "bbox": [0,10,10,20]},
    {"text": "15 CAPS", "confidence": 0.99, "bbox": [0,20,10,30]},
    {"text": "NO.6KM0039 MFDXJAN.26 EXP.DEC.27 M.R.P. 117.95", "confidence": 0.95, "bbox": [0,30,10,40]},
    {"text": "MADE IN INDIA", "confidence": 0.99, "bbox": [0,40,10,50]}
]
res_cipla = extractor.extract(blocks_cipla)
for d in res_cipla:
    if d.extraction_status == "FOUND" or d.extraction_status == "CONFLICTING":
        print(f"{d.field_name}: val={d.normalized_value}, raw={d.raw_value}")

# Test 2: GIROJAR (Regression)
print("\n=== GIROJAR ===")
blocks_girojar = [
    {"text": "Packed by Palji Bakery", "confidence": 0.99, "bbox": [0,0,10,10]},
    {"text": "SI ROASTED GIRI JAR", "confidence": 0.95, "bbox": [0,10,10,20]},
    {"text": "400 g", "confidence": 0.99, "bbox": [0,20,10,30]},
    {"text": "MRP Rs 160", "confidence": 0.98, "bbox": [0,30,10,40]},
    {"text": "Date Of Packing: 03-06-2026", "confidence": 0.95, "bbox": [0,40,10,50]},
    {"text": "Best Before: 3 Months", "confidence": 0.96, "bbox": [0,50,10,60]},
    {"text": "Produce of India", "confidence": 0.99, "bbox": [0,60,10,70]}
]
res_girojar = extractor.extract(blocks_girojar)
for d in res_girojar:
    if d.extraction_status == "FOUND" or d.extraction_status == "CONFLICTING":
        print(f"{d.field_name}: val={d.normalized_value}, raw={d.raw_value}")

# Test 3: MINIMALIST (New Test)
print("\n=== MINIMALIST ===")
blocks_minimal = [
    {"text": "Manufactured by Uprising Science Pvt. Ltd., F-2109, RIICO Ind.", "confidence": 0.99, "bbox": [0,0,10,10]},
    {"text": "ML No.: RAJ./COS-2825", "confidence": 0.95, "bbox": [0,10,10,20]},
    {"text": "30 ml", "confidence": 0.99, "bbox": [0,20,10,30]},
    {"text": "Country of Origin: India", "confidence": 0.99, "bbox": [0,30,10,40]},
    {"text": "For Consumer Complaints / Queries", "confidence": 0.98, "bbox": [0,40,10,50]},
    {"text": "contact@uprisingscience.com", "confidence": 0.97, "bbox": [0,51,10,61]},
    # Notice the MRP and dates are split!
    {"text": "MRP / Unit Sale Price / Batch No. / Mfg. Date / Exp. Date", "confidence": 0.95, "bbox": [0,60,10,70]},
    {"text": "Rs. 499  01/2026  01/2028", "confidence": 0.94, "bbox": [0,71,10,81]}
]
res_minimal = extractor.extract(blocks_minimal)
for d in res_minimal:
    if d.extraction_status == "FOUND" or d.extraction_status == "CONFLICTING":
        print(f"{d.field_name}: val={d.normalized_value}, raw={d.raw_value}")
