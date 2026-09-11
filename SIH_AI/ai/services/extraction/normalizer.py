import re

def normalize_ocr_text(text: str) -> str:
    """
    Safely normalizes OCR text to assist in heuristic matching without destroying original values.
    """
    if not text:
        return ""
        
    t = text.lower()
    
    # Handle known OCR squashing imperfections
    t = re.sub(r'countryoforigin', 'country of origin', t)
    t = re.sub(r'netqty', 'net qty', t)
    t = re.sub(r'consumercare', 'consumer care', t)
    t = re.sub(r'mfgdate', 'mfg date', t)
    
    # Strip common leading/trailing punctuation and spaces
    t = t.strip(' :;,-')
    
    return t
