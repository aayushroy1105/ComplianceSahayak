import re
from typing import Optional, Tuple, Any

def parse_quantity(text: str, norm_text: str) -> Tuple[str, Any, Optional[str], Optional[str]]:
    """
    Extracts Net Quantity.
    Returns: (status, normalized_value, normalized_unit, exact_raw_value)
    """
    # Look for patterns like "10 tablets", "500 ml", "1 kg"
    qty_pattern = re.compile(r'(\d+(?:\.\d+)?)\s*(mg|ml|g|kg|tablets|capsules|tabs|caps|pack)', re.IGNORECASE)
    match = qty_pattern.search(text)
    
    if match:
        val = float(match.group(1))
        unit = match.group(2).lower()
        exact_raw = match.group(0).strip()
        
        # normalize unit
        if unit in ['tabs', 'tablets']: unit = 'tablets'
        elif unit in ['caps', 'capsules']: unit = 'capsules'
        
        return ("FOUND", val, unit, exact_raw)
        
    return ("MISSING", None, None, None)
