import re

with open("services/extraction/parsers/entity_parser.py", "r") as f:
    entity_code = f.read()
    
# 1. Patch entity_parser.py (Address Truncation)
if "if raw_suffix:" in entity_code:
    new_suffix_code = """            if raw_suffix:
                # Address truncation
                address_markers = [' f-', ' plot ', ' road ', ' area ', ' industrial ', ' nagar ', ' jaipur ', ' district ', ' pin ', ' postal ']
                parts = raw_suffix.split(',')
                company_name = parts[0]
                for m in address_markers:
                    idx = company_name.lower().find(m)
                    if idx > 5:
                        company_name = company_name[:idx]
                        break
                val = company_name.strip()
                val = val.title() if val.islower() or val.isupper() else val
                return ("FOUND", val, None, val)"""
    
    # We replace from "if raw_suffix:" to the end of the return statement
    old_suffix_code = """            if raw_suffix:
                val = raw_suffix.title() if raw_suffix.islower() or raw_suffix.isupper() else raw_suffix
                return ("FOUND", val, None, raw_suffix)"""
                
    entity_code = entity_code.replace(old_suffix_code, new_suffix_code)
    with open("services/extraction/parsers/entity_parser.py", "w") as f:
        f.write(entity_code)


# 2. Patch general_parser.py (Consumer Care Aliases)
with open("services/extraction/parsers/general_parser.py", "r") as f:
    general_code = f.read()

old_care = 'aliases = ["consumer care", "customer care", "feedback"]'
new_care = 'aliases = ["consumer care", "customer care", "feedback", "consumer complaints", "complaints", "complaints / queries", "customer complaints", "queries", "consumer queries"]'
if old_care in general_code:
    general_code = general_code.replace(old_care, new_care)
    with open("services/extraction/parsers/general_parser.py", "w") as f:
        f.write(general_code)


# 3. Patch extractor.py (Product Name ML rejection + MRP/Date Multiline)
with open("services/extraction/extractor.py", "r") as f:
    extractor_code = f.read()

old_pn = """            if len(raw_text) > 5 and not "manufactured" in norm_text and not "marketed" in norm_text:
                if any(x in norm_text for x in ['ip', 'bp', 'usp', 'mg', 'ml', 'capsules', 'tablets']):
                    product_name_candidates.append((raw_text, conf, bbox))"""
new_pn = """            if len(raw_text) > 5 and not "manufactured" in norm_text and not "marketed" in norm_text:
                admin_terms = ['ml no', 'm.l. no', 'licence no', 'license no', 'fssai', 'batch no', 'lot no', 'mfg no', 'manufactured licence', 'manufacturing licence']
                if not any(t in norm_text for t in admin_terms):
                    if any(x in norm_text for x in ['ip', 'bp', 'usp', 'mg', 'ml', 'capsules', 'tablets']):
                        product_name_candidates.append((raw_text, conf, bbox))"""
extractor_code = extractor_code.replace(old_pn, new_pn)

old_mrp_date = """            # MRP
            status, n_val, n_unit, exact_raw = parse_mrp(raw_text, norm_text)
            if status != "MISSING":
                results["MRP"].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                
            # Quantity
            status, n_val, n_unit, exact_raw = parse_quantity(raw_text, norm_text)
            if status != "MISSING":
                results["NET_QUANTITY"].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                
            # Date
            for date_field in ["MANUFACTURING_DATE", "EXPIRY_DATE"]:
                status, n_val, n_unit, exact_raw = parse_date(raw_text, norm_text, date_field)
                if status != "MISSING":
                    results[date_field].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))"""

new_mrp_date = """            # MRP
            status, n_val, n_unit, exact_raw = parse_mrp(raw_text, norm_text)
            if status != "MISSING":
                results["MRP"].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
            else:
                if "mrp" in norm_text or "price" in norm_text or "rs" in norm_text:
                    for j in range(i + 1, min(len(blocks), i + 6)):
                        if is_spatially_close(bbox, blocks[j].get('bbox', None)):
                            combined = raw_text + " " + blocks[j]['text']
                            s, nv, nu, ex = parse_mrp(combined, normalize_ocr_text(combined))
                            if s != "MISSING":
                                results["MRP"].append((s, nv, nu, ex or combined, conf, blocks[j].get('bbox', None)))
                                break
                
            # Quantity
            status, n_val, n_unit, exact_raw = parse_quantity(raw_text, norm_text)
            if status != "MISSING":
                results["NET_QUANTITY"].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                
            # Date
            for date_field in ["MANUFACTURING_DATE", "EXPIRY_DATE"]:
                status, n_val, n_unit, exact_raw = parse_date(raw_text, norm_text, date_field)
                if status != "MISSING":
                    results[date_field].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                else:
                    date_aliases = ["mfg", "pkd", "packed", "mf", "mfd", "exp", "expiry", "use before", "best before"]
                    if any(a in norm_text for a in date_aliases):
                        for j in range(i + 1, min(len(blocks), i + 6)):
                            if is_spatially_close(bbox, blocks[j].get('bbox', None)):
                                combined = raw_text + " " + blocks[j]['text']
                                s, nv, nu, ex = parse_date(combined, normalize_ocr_text(combined), date_field)
                                if s != "MISSING":
                                    results[date_field].append((s, nv, nu, ex or combined, conf, blocks[j].get('bbox', None)))
                                    break"""

extractor_code = extractor_code.replace(old_mrp_date, new_mrp_date)

with open("services/extraction/extractor.py", "w") as f:
    f.write(extractor_code)
print("Patched all fixes")
