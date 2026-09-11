from typing import List, Dict, Any, Tuple
from schemas.base import Declaration, Product

class ProductClassifier:
    """
    Heuristic-based Product Classifier.
    Designed to be a drop-in replacement for a future ML model.
    """
    TAXONOMY = [
        "FOOD", "COSMETIC", "HOUSEHOLD", "GARMENT", 
        "ELECTRONICS", "GENERAL_COMMODITY", "UNKNOWN"
    ]
    
    KEYWORD_MAP = {
        "FOOD": ["fssai", "ingredients", "nutritional", "kcal", "protein", "carbohydrate", "sugar", "fat", "edible", "snack", "food", "beverage"],
        "COSMETIC": ["skin", "hair", "face", "cosmetic", "external use only", "cream", "lotion", "shampoo", "soap", "fragrance"],
        "HOUSEHOLD": ["detergent", "cleaner", "wash", "floor", "toilet", "household", "surface", "disinfectant"],
        "GARMENT": ["cotton", "polyester", "size", "wash care", "apparel", "shirt", "trouser", "garment", "woven", "knit", "fabric"],
        "ELECTRONICS": ["voltage", "watt", "hz", "electronic", "appliance", "warranty", "model", "serial", "ac", "dc", "battery"]
    }

    def classify(self, declarations: List[Declaration], ocr_blocks: List[Dict[str, Any]]) -> Product:
        scores = {category: 0.0 for category in self.TAXONOMY if category != "UNKNOWN"}
        found_signals = []
        
        # Build a unified text corpus from OCR blocks for keyword searching
        corpus = " ".join([block.get("text", "").lower() for block in ocr_blocks])
        
        # 1. Search raw corpus for keywords
        for category, keywords in self.KEYWORD_MAP.items():
            for kw in keywords:
                if kw in corpus:
                    scores[category] += 1.0
                    found_signals.append(f"keyword:{kw}")
                    
        # 2. Check declarations for specific signals
        product_name = None
        for decl in declarations:
            if decl.field_name == "PRODUCT_NAME" and decl.extraction_status == "FOUND":
                product_name = decl.raw_value
                found_signals.append("decl:PRODUCT_NAME")
                
        # 3. Determine best category and handle conflicts
        # A conflict is when multiple distinct categories have strong scores (>= 2.0)
        strong_categories = [cat for cat, score in scores.items() if score >= 2.0]
        
        if len(strong_categories) > 1:
            best_category = "UNKNOWN"
            confidence = 0.0
            found_signals.append("conflict:multiple_strong_signals")
        else:
            best_category = "UNKNOWN"
            best_score = 0.0
            
            for category, score in scores.items():
                if score > best_score:
                    best_score = score
                    best_category = category
                    
            confidence = 0.0
            if best_score >= 2.0:
                confidence = 0.90
            elif best_score >= 1.0:
                confidence = 0.60
                
            if best_category == "UNKNOWN":
                best_category = "GENERAL_COMMODITY"
                confidence = 0.30
                found_signals.append("heuristic:fallback_to_general_commodity")
                
        # Naive fallback for PRODUCT_NAME
        if not product_name and ocr_blocks:
            ignore_keywords = ["mrp", "rs", "net qty", "quantity", "mfd", "mfg", "pack", "import", "custom", "care", "ingredient", "nutri", "date", "batch", "weight"]
            for block in ocr_blocks:
                t = block.get('text', '').lower()
                if len(t) > 3 and not any(k in t for k in ignore_keywords):
                    product_name = block.get('text')
                    found_signals.append("heuristic:first_non_keyword_block")
                    
                    # Update the declarations list to include the inferred product name!
                    for decl in declarations:
                        if decl.field_name == "PRODUCT_NAME":
                            decl.extraction_status = "FOUND"
                            decl.raw_value = product_name
                            decl.normalized_value = product_name
                            decl.confidence = block.get('confidence', 0.5)
                            break
                    break
            
        return Product(
            product_name=product_name,
            product_category=best_category,
            classification_confidence=confidence,
            signals=found_signals,
            classification_method="HEURISTIC"
        )
