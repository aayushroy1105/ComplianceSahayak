import re
from typing import Optional, Tuple, Any

def parse_general(text: str, norm_text: str, field_name: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts Country of Origin and Consumer Care.
    Returns: (status, normalized_value, normalized_unit, exact_raw_value)
    """
    if field_name == "COUNTRY_OF_ORIGIN":
        aliases = ["country of origin", "made in", "produce of", "product of", "manufactured in"]
        for a in aliases:
            if a in norm_text:
                suffix = norm_text.split(a)[-1].strip(' :;-')
                if suffix:
                    # extract just the first few words or the country name
                    clean = re.sub(r'[^a-zA-Z\s]', '', suffix).strip()
                    if clean:
                        return ("FOUND", clean.title(), None, clean)
        
        # Conservative INDIA extraction fallback
        match = re.search(r'\b(india)\b', text, re.IGNORECASE)
        if match:
            return ("FOUND", "India", None, match.group(1))
            
        return ("UNCERTAIN", None, None, None)
    elif field_name == "CONSUMER_CARE":
        aliases = ["consumer care", "customer care", "feedback"]
        for a in aliases:
            if a in norm_text:
                suffix = norm_text.split(a)[-1].strip(' :;-')
                if suffix:
                    val = text.split(':')[-1].strip() if ':' in text else suffix
                    return ("FOUND", val, None, val)
                return ("UNCERTAIN", None, None, None)
                
    elif field_name == "PRODUCT_NAME":
        return ("MISSING", None, None, None)
        
    return ("MISSING", None, None, None)
