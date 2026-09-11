from typing import List, Dict, Any
from schemas.base import Declaration
from services.extraction.normalizer import normalize_ocr_text
from services.extraction.parsers.mrp_parser import parse_mrp
from services.extraction.parsers.quantity_parser import parse_quantity
from services.extraction.parsers.date_parser import parse_date
from services.extraction.parsers.entity_parser import parse_entity
from services.extraction.parsers.general_parser import parse_general

def is_spatially_close(bbox1, bbox2):
    if not bbox1 or not bbox2:
        return True # Fallback if bounding boxes are missing
    
    x1_min, y1_min, x1_max, y1_max = bbox1
    x2_min, y2_min, x2_max, y2_max = bbox2
    
    # Check vertical distance (allowing slight overlap or gap)
    vertical_diff = y2_min - y1_max
    is_below = -15 <= vertical_diff <= 80
    
    # Check horizontal alignment
    is_same_line = abs(y1_min - y2_min) < 30 and -15 < (x2_min - x1_max) < 150
    is_next_line_aligned = is_below and abs(x1_min - x2_min) < 150
    
    return is_same_line or is_next_line_aligned

class DeclarationExtractor:
    def __init__(self):
        self.fields = [
            "MANUFACTURER", "PACKER", "IMPORTER", "PRODUCT_NAME",
            "NET_QUANTITY", "MRP", "MANUFACTURING_DATE", "EXPIRY_DATE", "COUNTRY_OF_ORIGIN", "CONSUMER_CARE"
        ]

    def extract(self, blocks: List[Dict[str, Any]], image_id: str = "img1") -> List[Declaration]:
        results = {f: [] for f in self.fields}
        
        # Product name needs a holistic view
        # We will collect possible product names, preferring ones with "mg" or "capsules"
        product_name_candidates = []
        
        for i, block in enumerate(blocks):
            raw_text = block['text']
            conf = block['confidence']
            bbox = block.get('bbox', None)
            
            norm_text = normalize_ocr_text(raw_text)
            
            # MRP
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
                    results[date_field].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                
            # Entities
            for ent in ["MANUFACTURER", "PACKER", "IMPORTER"]:
                status, n_val, n_unit, exact_raw = parse_entity(raw_text, norm_text, ent)
                if status == "FOUND":
                    results[ent].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                else:
                    # Try multiline context
                    next_block = None
                    for j in range(i + 1, min(len(blocks), i + 6)):
                        if is_spatially_close(bbox, blocks[j].get('bbox', None)):
                            next_block = blocks[j]
                            break
                            
                    next_raw = next_block['text'] if next_block else ""
                    if next_raw:
                        combined_raw = raw_text + "\n" + next_raw
                        combined_norm = normalize_ocr_text(combined_raw)
                        status_m, n_val_m, n_unit_m, exact_raw_m = parse_entity(combined_raw, combined_norm, ent)
                        if status_m != "MISSING":
                            results[ent].append((status_m, n_val_m, n_unit_m, exact_raw_m or combined_raw, conf, bbox))
                        elif status != "MISSING":
                            results[ent].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                    elif status != "MISSING":
                        results[ent].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
                    
            # General
            for gen in ["COUNTRY_OF_ORIGIN", "CONSUMER_CARE"]:
                status, n_val, n_unit, exact_raw = parse_general(raw_text, norm_text, gen)
                if status != "MISSING":
                    results[gen].append((status, n_val, n_unit, exact_raw or raw_text, conf, bbox))
            
            # Collect PRODUCT_NAME candidates
            # Very simple heuristic: it often contains 'IP', 'mg', 'ml', 'capsule', 'tablet'
            if len(raw_text) > 5 and not "manufactured" in norm_text and not "marketed" in norm_text:
                if any(x in norm_text for x in ['ip', 'bp', 'usp', 'mg', 'ml', 'capsules', 'tablets']):
                    product_name_candidates.append((raw_text, conf, bbox))

        # Sort product name candidates: favor those containing 'mg' or 'capsule'
        if product_name_candidates:
            # Sort by a score: +1 for mg, +1 for capsule/tablet, +1 for length > 15
            def score_pn(text):
                s = 0
                lt = text.lower()
                if 'mg' in lt or 'ml' in lt: s += 1
                if 'capsule' in lt or 'tablet' in lt: s += 1
                if len(lt) > 15: s += 1
                return s
                
            product_name_candidates.sort(key=lambda x: score_pn(x[0]), reverse=True)
            best_pn = product_name_candidates[0]
            # Strip leading asterisks
            pn_text = best_pn[0].lstrip('* ')
            results["PRODUCT_NAME"].append(("FOUND", pn_text, None, pn_text, best_pn[1], best_pn[2]))
            
        # Consolidate results
        declarations = []
        for field in self.fields:
            candidates = results[field]
            if not candidates:
                declarations.append(Declaration(
                    field_name=field,
                    extraction_status="MISSING",
                    confidence=0.0
                ))
            elif len(candidates) == 1:
                c = candidates[0]
                declarations.append(Declaration(
                    field_name=field,
                    extraction_status=c[0],
                    normalized_value=c[1],
                    normalized_unit=c[2],
                    raw_value=c[3],
                    confidence=c[4],
                    bounding_box=c[5],
                    source_image_id=image_id
                ))
            else:
                # Multiple candidates
                valid_candidates = [c for c in candidates if c[0] == "FOUND"]
                if not valid_candidates:
                    declarations.append(Declaration(
                        field_name=field,
                        extraction_status="UNCERTAIN",
                        raw_value=" | ".join([x[3] for x in candidates]),
                        confidence=min([x[4] for x in candidates])
                    ))
                    continue
                    
                # Check if all valid candidates agree on normalized value
                first_val = valid_candidates[0][1]
                conflict = any(c[1] != first_val for c in valid_candidates)
                
                if conflict:
                    declarations.append(Declaration(
                        field_name=field,
                        extraction_status="CONFLICTING",
                        raw_value=" | ".join([c[3] for c in valid_candidates]),
                        confidence=min([c[4] for c in valid_candidates]),
                        source_image_id=image_id
                    ))
                else:
                    c = valid_candidates[0]
                    declarations.append(Declaration(
                        field_name=field,
                        extraction_status="FOUND",
                        normalized_value=c[1],
                        normalized_unit=c[2],
                        raw_value=c[3],
                        confidence=c[4],
                        bounding_box=c[5],
                        source_image_id=image_id
                    ))
                    
        return declarations
