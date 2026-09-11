import re
from typing import Optional, Tuple, Any

def parse_mrp(text: str, norm_text: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts MRP using robust regex.
    Returns: (status, normalized_value, normalized_unit, exact_raw_value)
    """
    # Exclude common false positives
    false_positives = ['colours', 'color', 'warning', 'schedule', 'caution']
    for fp in false_positives:
        if fp in norm_text:
            return ("MISSING", None, None, None)
            
    mrp_pattern = re.compile(r'\b(?:m\.?r\.?p\.?|rs\.?|₹|inr)\s*[:\.]?\s*(\d+\.?\d*)', re.IGNORECASE)
    match = mrp_pattern.search(text)
    if match:
        val = float(match.group(1))
        # basic sanity check for MRP
        if 0 < val < 50000:
            exact_raw = match.group(0).strip()
            return ("FOUND", val, "INR", exact_raw)
            
    return ("MISSING", None, None, None)
