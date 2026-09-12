import re
from typing import Optional, Tuple, Any

def parse_date(text: str, norm_text: str, field_name: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts Date.
    Returns: (status, normalized_value, normalized_unit, exact_raw_value)
    """
    if field_name == "MANUFACTURING_DATE":
        aliases = ["mfg", "mfg date", "manufacturing date", "date of manufacture", "pkd", "packed on", "mf", "mfd"]
    elif field_name == "EXPIRY_DATE":
        aliases = ["exp", "exp.", "exp date", "expiry", "use before", "use by", "best before"]
    else:
        return ("MISSING", None, None, None)
    
    # Check if the block actually contains the specific alias
    if not any(a in norm_text for a in aliases):
        return ("MISSING", None, None, None)
        
    exact_raw = text.strip()

    # Matches DD/MM/YYYY, MM/YYYY, DD-MM-YYYY, etc.
    match = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', norm_text)
    if match:
        return ("FOUND", f"{match.group(3)}-{match.group(2)}-{match.group(1)}", None, exact_raw)
        
    match = re.search(r'(\d{2})[-/](\d{4})', norm_text)
    if match:
        return ("FOUND", f"{match.group(2)}-{match.group(1)}", None, exact_raw)
        
    # Matches MMM YY or MMM YYYY (e.g. JAN 26, DEC 2027)
    months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", 
              "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
    
    matches = list(re.finditer(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\.-]+(\d{2,4})\b', norm_text, re.IGNORECASE))
    if matches:
        alias_pos = -1
        for a in aliases:
            pos = norm_text.find(a)
            if pos != -1:
                alias_pos = pos
                break
                
        best_match = matches[0]
        if len(matches) > 1 and alias_pos != -1:
            for m in matches:
                if m.start() > alias_pos:
                    best_match = m
                    break
                    
        month = months[best_match.group(1).lower()]
        year = best_match.group(2)
        if len(year) == 2:
            year = "20" + year
        return ("FOUND", f"{year}-{month}", None, exact_raw)
        
    return ("MISSING", None, None, None)
