import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List

class BlueprintAnalyzer:
    """
    Module 7: Infrastructure Compliance Assistance.
    Analyzes architectural floor plans, blueprints, and laboratory drawings.
    Uses edge detection and contour analysis to verify room layouts, carpet areas, and lab dimensions.
    """
    def __init__(self, pixels_per_meter: float = 30.0):
        self.pixels_per_meter = pixels_per_meter

    def analyze_floor_plan(self, pil_image: Image.Image) -> Dict[str, Any]:
        """
        Processes raster blueprint to detect distinct instructional rooms and compute carpet area.
        """
        img_np = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Binarize floor plan
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to close wall gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours of individual rooms
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_rooms = []
        total_sqm = 0.0
        
        for c in contours:
            area_px = cv2.contourArea(c)
            # Filter noise and entire outer perimeter
            if 1500 < area_px < 500000:
                sqm = area_px / (self.pixels_per_meter ** 2)
                x, y, w, h = cv2.boundingRect(c)
                dim_w = round(w / self.pixels_per_meter, 2)
                dim_h = round(h / self.pixels_per_meter, 2)
                
                # Check AICTE minimum classroom norms: >= 66 sqm
                is_compliant_classroom = sqm >= 66.0
                detected_rooms.append({
                    "room_id": f"ROOM-{len(detected_rooms)+1}",
                    "area_sqm": round(sqm, 2),
                    "dimensions_m": f"{dim_w}m x {dim_h}m",
                    "meets_min_classroom_norm": is_compliant_classroom,
                    "bbox": [int(x), int(y), int(w), int(h)]
                })
                total_sqm += sqm

        return {
            "rooms_detected_count": len(detected_rooms),
            "computed_carpet_area_sqm": round(total_sqm, 2),
            "rooms": detected_rooms[:12],
            "geometry_verified": len(detected_rooms) > 0
        }
