with open("services/extraction/parsers/date_parser.py", "r") as f:
    content = f.read()

old_sort = """    # Pick the best candidate based on alias position
    best_candidate = candidates[0]
    if len(candidates) > 1 and alias_pos != -1:
        # Sort candidates by how close they are to the alias, but only those AFTER the alias
        valid_cands = [c for c in candidates if c[2] >= alias_pos - 4]
        if valid_cands:
            # Sort by positive distance from alias_pos
            valid_cands.sort(key=lambda x: x[2] - alias_pos)
            best_candidate = valid_cands[0]
            
    return ("FOUND", best_candidate[0], None, best_candidate[1])"""

new_sort = """    # Pick the best candidate based on alias position
    best_candidate = candidates[0]
    
    if len(candidates) > 1:
        # If we are looking for EXPIRY, and multiple dates are present, it's safer to pick the latest date
        # (Assuming the block contains Mfg and Exp dates)
        # Dates are returned in YYYY-MM format, so alphabetical sorting works perfectly!
        sorted_by_date = sorted(candidates, key=lambda x: x[0])
        
        if field_name == "EXPIRY_DATE":
            best_candidate = sorted_by_date[-1] # Latest date
        elif field_name == "MANUFACTURING_DATE":
            best_candidate = sorted_by_date[0] # Earliest date
            
    return ("FOUND", best_candidate[0], None, best_candidate[1])"""

content = content.replace(old_sort, new_sort)
with open("services/extraction/parsers/date_parser.py", "w") as f:
    f.write(content)
print("date patched 2")
