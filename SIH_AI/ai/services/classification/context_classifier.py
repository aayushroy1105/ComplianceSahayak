from typing import List, Dict, Any, Tuple
from schemas.base import Declaration, PackageContext

class ContextClassifier:
    """
    Heuristic-based Package Context Classifier.
    """
    TAXONOMY = [
        "RETAIL", "WHOLESALE", "IMPORTED", "DOMESTIC", 
        "EXPORT", "INDUSTRIAL", "INSTITUTIONAL", 
        "EXEMPT", "SPECIAL_CATEGORY", "UNKNOWN"
    ]
    
    def classify(self, declarations: List[Declaration], ocr_blocks: List[Dict[str, Any]]) -> PackageContext:
        corpus = " ".join([block.get("text", "").lower() for block in ocr_blocks])
        
        scores = {category: 0.0 for category in self.TAXONOMY if category != "UNKNOWN"}
        relevant_metadata = {}
        
        # 1. Check declarations for explicit context signals
        has_mrp = False
        has_importer = False
        
        for decl in declarations:
            if decl.field_name == "MRP" and decl.extraction_status == "FOUND":
                has_mrp = True
            elif decl.field_name == "IMPORTER" and decl.extraction_status == "FOUND":
                has_importer = True
            elif decl.field_name == "COUNTRY_OF_ORIGIN" and decl.extraction_status == "FOUND":
                if decl.normalized_value and decl.normalized_value.lower() not in ["india", "bharat"]:
                    scores["IMPORTED"] += 1.0
                    relevant_metadata["coo_signal"] = decl.normalized_value

        # MRP is merely a retail signal, not absolute proof
        if has_mrp:
            scores["RETAIL"] += 1.0
            relevant_metadata["mrp_signal"] = True
            
        # Importer is a signal, not absolute proof
        if has_importer:
            scores["IMPORTED"] += 1.0
            relevant_metadata["importer_signal"] = True
            
        # 2. Text based heuristics
        if "for export only" in corpus or "not for sale in india" in corpus:
            scores["EXPORT"] += 3.0
            
        if "wholesale" in corpus or "not for retail sale" in corpus:
            scores["WHOLESALE"] += 2.0
            scores["RETAIL"] = 0.0 # Strict override of MRP signal
            
        if "industrial use" in corpus or "institutional" in corpus:
            scores["INDUSTRIAL"] += 2.0
            scores["RETAIL"] = 0.0 # Strict override of MRP signal

        if "retail" in corpus or "consumer" in corpus:
            scores["RETAIL"] += 1.0

        # Determine best context
        best_context = "UNKNOWN"
        best_score = 0.0
        
        for category, score in scores.items():
            if score > best_score:
                best_score = score
                best_context = category
                
        # Calculate confidence using conservative thresholds
        # A single weak signal (score < 1.0) remains UNKNOWN rather than guessing
        confidence = 0.0
        if best_score >= 2.0:
            confidence = 0.90
        elif best_score >= 1.0:
            confidence = 0.60
        else:
            best_context = "UNKNOWN"
            
        if best_context == "UNKNOWN":
            confidence = 0.0

        return PackageContext(
            package_context=best_context,
            context_confidence=confidence,
            relevant_metadata=relevant_metadata if relevant_metadata else None
        )
