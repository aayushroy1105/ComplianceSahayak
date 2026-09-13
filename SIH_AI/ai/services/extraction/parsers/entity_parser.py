import re
from typing import Optional, Tuple, Any

def parse_entity(text: str, norm_text: str, entity_type: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts Entities (Manufacturer, Packer, Importer).
    Returns: (status, normalized_value, normalized_unit, exact_raw_value)
    """
    aliases = []
    if entity_type == "MANUFACTURER":
        aliases = ["manufactured & marketed by", "manufactured by", "manufacturer", "manufactured in india by", "mfd by", "mfd. by", "mfg by", "mfg. by", "mfd under", "mfd. under"]
    elif entity_type == "PACKER":
        aliases = ["packed by", "packer", "pkd by", "pkd. by"]
    elif entity_type == "IMPORTER":
        aliases = ["imported by", "importer", "imp by", "imp. by"]
        
    matched_alias = None
    for a in aliases:
        if a in norm_text:
            matched_alias = a
            break
            
    if not matched_alias:
        return ("MISSING", None, None, None)
        
    idx = norm_text.find(matched_alias)
    if idx != -1:
        match = re.search(re.escape(matched_alias), text, re.IGNORECASE)
        if match:
            raw_suffix = text[match.end():].strip(' :;-\n\r')
            
            if matched_alias in ["mfd under", "mfd. under"]:
                by_match = re.search(r'\bby\b', raw_suffix, re.IGNORECASE)
                if by_match:
                    raw_suffix = raw_suffix[by_match.end():].strip(' :;-\n\r')
                else:
                    return ("MISSING", None, None, None)

            if raw_suffix:
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
                return ("FOUND", val, None, val)
            
    return ("UNCERTAIN", None, None, None)
