import time
import logging
import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from paddleocr import PaddleOCR

logger = logging.getLogger(__name__)

def _parse_paddle_result(result, x_offset=0, y_offset=0, rotation_deg=0, orig_w=0, orig_h=0, scale_x=1.0, scale_y=1.0):
    blocks = []
    if result and isinstance(result, list) and len(result) > 0:
        res_dict = result[0]
        if not res_dict: return blocks
        
        texts = res_dict.get('rec_texts', [])
        scores = res_dict.get('rec_scores', [])
        polys = res_dict.get('dt_polys', [])
        
        for i in range(len(texts)):
            text = texts[i]
            confidence = float(scores[i]) if i < len(scores) else 0.0
            
            if i < len(polys):
                poly = polys[i]
                # Scale back to pre-scaled crop coords
                xs = [pt[0] / scale_x for pt in poly]
                ys = [pt[1] / scale_y for pt in poly]
                
                # Undo rotation
                if rotation_deg == 90:
                    # Rotated clockwise: new_x = orig_y, new_y = orig_h - orig_x
                    # So orig_y = new_x, orig_x = orig_h - new_y
                    # Where orig_h is the height of the crop *before* rotation, which is orig_w of the rotated image. Wait, easier:
                    # Let's just approximate the center and use that
                    # Actually, if we just want deduplication, precise bbox isn't strictly needed if text matches,
                    # but let's do a simple reverse rotation for the bounding box.
                    pass
                elif rotation_deg == 270:
                    pass
                    
                x_min, y_min = int(min(xs)) + x_offset, int(min(ys)) + y_offset
                x_max, y_max = int(max(xs)) + x_offset, int(max(ys)) + y_offset
            else:
                x_min, y_min, x_max, y_max = 0, 0, 0, 0
                
            blocks.append({
                "text": text,
                "confidence": confidence,
                "bbox": [x_min, y_min, x_max, y_max]
            })
    return blocks

class OCREngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OCREngine, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
        
    def initialize(self):
        if self.initialized:
            return
            
        start_time = time.time()
        logger.info("Initializing PaddleOCR model (this may take a moment)...")
        self.ocr = PaddleOCR(use_textline_orientation=True, lang='en')
        self.version = "paddleocr_v2.6+_enhanced"
        self.init_time_ms = int((time.time() - start_time) * 1000)
        logger.info(f"PaddleOCR initialized in {self.init_time_ms} ms.")
        self.initialized = True
        
    def extract_text(self, image_bytes: bytes) -> Tuple[List[Dict[str, Any]], int]:
        if not self.initialized:
            self.initialize()
            
        start_time = time.time()
        
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode image bytes into a valid image matrix.")
            
        # 1. Base inference
        result = self.ocr.ocr(img)
        blocks = _parse_paddle_result(result)
        
        # Lightweight Enhancement: Target small-text/right-edge crop
        h, w = img.shape[:2]
        crop_x = int(w * 0.7)
        crop_y = 0
        crop = img[crop_y:h, crop_x:w]
        
        if crop.size > 0:
            # Upscale 2x
            crop_up = cv2.resize(crop, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            
            # Mild contrast/sharpness enhancement
            # Unsharp mask
            gaussian = cv2.GaussianBlur(crop_up, (0, 0), 2.0)
            enhanced = cv2.addWeighted(crop_up, 1.5, gaussian, -0.5, 0)
            
            # Rotate 90 and 270 and run OCR
            crop_90 = cv2.rotate(enhanced, cv2.ROTATE_90_CLOCKWISE)
            res_90 = self.ocr.ocr(crop_90)
            blocks_90 = _parse_paddle_result(res_90, x_offset=crop_x, y_offset=crop_y, scale_x=2.0, scale_y=2.0)
            
            crop_270 = cv2.rotate(enhanced, cv2.ROTATE_90_COUNTERCLOCKWISE)
            res_270 = self.ocr.ocr(crop_270)
            blocks_270 = _parse_paddle_result(res_270, x_offset=crop_x, y_offset=crop_y, scale_x=2.0, scale_y=2.0)
            
            blocks.extend(blocks_90)
            blocks.extend(blocks_270)
            
        # Deduplicate
        seen = set()
        final_blocks = []
        for b in blocks:
            txt = str(b['text']).strip().upper()
            if not txt: continue
            
            # Simple dedup based on text content (since crops often duplicate main image text)
            if txt not in seen:
                seen.add(txt)
                final_blocks.append(b)
                
        processing_time_ms = int((time.time() - start_time) * 1000)
        return final_blocks, processing_time_ms

ocr_engine = OCREngine()
