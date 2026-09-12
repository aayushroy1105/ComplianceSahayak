import re
from typing import Optional, Tuple, Any

def parse_date(text: str, norm_text: str, field_name: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts Date.
    Returns: (status, normalized_value, normalized_unit, exact_raw_value)
    """
    if field_name == "MANUFACTURING_DATE":
        aliases = ["mfg", "mfg date", "manufacturing date", "date of manufacture", "date of packing", "pkd", "packed on", "mf", "mfd"]
    elif field_name == "EXPIRY_DATE":
        aliases = ["exp", "exp.", "exp date", "expiry", "use before", "use by", "best before"]
    else:
        return ("MISSING", None, None, None)
    
    # Check if the block actually contains the specific alias
    if not any(a in norm_text for a in aliases):
        return ("MISSING", None, None, None)
        
    # Track the exact matched string instead of full block
    best_exact_raw = text.strip()

    # Matches DD/MM/YYYY, MM/YYYY, DD-MM-YYYY, etc.
    match = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', norm_text)
    if match:
        orig_match = re.search(r'(\d{2})[-/](\d{2})[-/](\d{4})', text)
        if orig_match:
            best_exact_raw = orig_match.group(0)
        return ("FOUND", f"{match.group(3)}-{match.group(2)}-{match.group(1)}", None, best_exact_raw)
        
    match = re.search(r'(\d{2})[-/](\d{4})', norm_text)
    if match:
        orig_match = re.search(r'(\d{2})[-/](\d{4})', text)
        if orig_match:
            best_exact_raw = orig_match.group(0)
        return ("FOUND", f"{match.group(2)}-{match.group(1)}", None, best_exact_raw)
        
    # Matches MMM YY or MMM YYYY (e.g. JAN 26, DEC 2027)
    months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06", 
              "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
    
    # Find all dates in the text
    matches = list(re.finditer(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*[\s\.-]+(\d{2,4})\b', text, re.IGNORECASE))
    if matches:
        # Find which alias is associated with this field
        alias_pos = -1
        best_alias_len = 0
        
        for a in aliases:
            # We search in norm_text, but need to map to text. Let's just search in text case-insensitive
            m_alias = re.search(re.escape(a), text, re.IGNORECASE)
            # Or handle spaces missing in text by stripping spaces in regex? 
            # Actually norm_text is what we checked earlier. Let's find first alias occurrence in text.
            
            # Simple approach: search in text lowercased without punctuation?
            # We know it's in norm_text. Let's just find the alias in norm_text and assume rough position
            pos = norm_text.find(a)
            if pos != -1:
                if len(a) > best_alias_len:
                    alias_pos = pos
                    best_alias_len = len(a)
                
        best_match = matches[0]
        if len(matches) > 1 and alias_pos != -1:
            # If multiple dates, pick the one immediately following the matched alias
            # We map alias_pos from norm_text to an approximate position in text
            # Just pick the first date whose start() in text is > roughly the alias pos
            # Since norm_text strips some punctuation, text start() is usually >= norm_text pos
            for m in matches:
                # scale alias_pos slightly if needed, but text length >= norm_text length usually
                if m.start() >= alias_pos * 0.8: 
                    best_match = m
                    break
                    
        month = months[best_match.group(1).lower()]
        year = best_match.group(2)
        if len(year) == 2:
            year = "20" + year
            
        return ("FOUND", f"{year}-{month}", None, best_match.group(0))
        
    # Handle "Best Before: X Months"
    if field_name == "EXPIRY_DATE" and "best before" in norm_text:
        match = re.search(r'(\d+)\s*(months|years|days)', text, re.IGNORECASE)
        if match:
            return ("FOUND", match.group(0), None, match.group(0))

    return ("MISSING", None, None, None)
