import re
from typing import Optional, Tuple, Any

def parse_date(text: str, norm_text: str, field_name: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts Date.
    """
    if field_name == "MANUFACTURING_DATE":
        aliases = ["mfg", "mfg date", "manufacturing date", "date of manufacture", "date of packing", "pkd", "packed on", "mf", "mfd"]
    elif field_name == "EXPIRY_DATE":
        aliases = ["exp", "exp.", "exp date", "expiry", "use before", "use by", "best before"]
    else:
        return ("MISSING", None, None, None)
    
    if not any(a in norm_text for a in aliases):
        return ("MISSING", None, None, None)
        
    best_exact_raw = text.strip()
    
    # We will collect all date candidates
    candidates = [] # (normalized_val, exact_raw, start_pos_in_text)
    
    # 1. DD/MM/YYYY
    for match in re.finditer(r'(\d{2})[-/](\d{2})[-/](\d{4})', text):
        candidates.append((f"{match.group(3)}-{match.group(2)}-{match.group(1)}", match.group(0), match.start()))
        
    # 2. MM/YYYY
    for match in re.finditer(r'(?<!\d[-/])(\d{2})[-/](\d{4})', text):
        candidates.append((f"{match.group(2)}-{match.group(1)}", match.group(0), match.start()))
        
    # 3. MMM YY or MMM YYYY
    months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", 
              "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
    for match in re.finditer(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\.-]+(\d{2,4})\b', text, re.IGNORECASE):
        month = months[match.group(1).lower()]
        year = match.group(2)
        if len(year) == 2: year = "20" + year
        candidates.append((f"{year}-{month}", match.group(0), match.start()))
        
    # 4. Best before X months
    if field_name == "EXPIRY_DATE" and "best before" in norm_text:
        match = re.search(r'(\d+)\s*(months|years|days)', text, re.IGNORECASE)
        if match:
            candidates.append((match.group(0), match.group(0), match.start()))

    if not candidates:
        return ("MISSING", None, None, None)
        
    # Find alias position in text
    alias_pos = -1
    best_alias_len = 0
    for a in aliases:
        # Search for alias in original text (ignoring case)
        match = re.search(re.escape(a).replace(r'\ ', r'[\s\.\-\/]*'), text, re.IGNORECASE)
        if match:
            if len(a) > best_alias_len:
                alias_pos = match.start()
                best_alias_len = len(a)
                
    if alias_pos == -1:
        # If we couldn't match alias in exact text, fallback to norm_text pos
        for a in aliases:
            pos = norm_text.find(a)
            if pos != -1 and len(a) > best_alias_len:
                alias_pos = pos
                best_alias_len = len(a)

    # Pick the best candidate based on alias position
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
            
    return ("FOUND", best_candidate[0], None, best_candidate[1])
