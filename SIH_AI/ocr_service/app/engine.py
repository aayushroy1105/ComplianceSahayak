import time
import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

class OCREngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCREngine, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
        
    def initialize(self):
        """Loads the PaddleOCR model into memory exactly once."""
        if self.initialized:
            return
            
        start_time = time.time()
        logger.info("Initializing PaddleOCR model (this may take a moment)...")
        # Initialize PaddleOCR with English language. 
        # use_textline_orientation=True helps with rotated text detection.
        self.ocr = PaddleOCR(use_textline_orientation=True, lang='en')
        self.version = "paddleocr_v2.6+" # Generalized for contract compatibility
        self.init_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"PaddleOCR initialized in {self.init_time_ms} ms.")
        self.initialized = True
        
    def extract_text(self, image_bytes: bytes) -> Tuple[List[Dict[str, Any]], int]:
        """
        Executes real OCR inference on the provided image bytes.
        Returns the parsed text blocks and processing time in ms.
        """
        if not self.initialized:
            self.initialize()
            
        start_time = time.time()
        
        # Convert raw bytes to numpy array suitable for OpenCV/Paddle
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image bytes into a valid image matrix.")
            
        # Run PaddleOCR Inference
        # Result format: [[[[x1,y1],[x2,y2],[x3,y3],[x4,y4]], ("text", confidence)], ...]
        result = self.ocr.ocr(img)
        
        blocks = []
        if result and isinstance(result, list) and len(result) > 0:
            res_dict = result[0]
            
            # v3.7 (paddlex backend) returns a dictionary with 'rec_texts', 'rec_scores', 'dt_polys'
            texts = res_dict.get('rec_texts', [])
            scores = res_dict.get('rec_scores', [])
            polys = res_dict.get('dt_polys', [])
            
            for i in range(len(texts)):
                text = texts[i]
                confidence = float(scores[i]) if i < len(scores) else 0.0
                
                # Extract bounding box from polygon
                if i < len(polys):
                    poly = polys[i]
                    xs = [pt[0] for pt in poly]
                    ys = [pt[1] for pt in poly]
                    x_min, y_min = int(min(xs)), int(min(ys))
                    x_max, y_max = int(max(xs)), int(max(ys))
                else:
                    x_min, y_min, x_max, y_max = 0, 0, 0, 0
                    
                blocks.append({
                    "text": text,
                    "confidence": confidence,
                    "bbox": [x_min, y_min, x_max, y_max]
                })
                
        processing_time_ms = int((time.time() - start_time) * 1000)
        return blocks, processing_time_ms

# Global singleton instance
ocr_engine = OCREngine()
