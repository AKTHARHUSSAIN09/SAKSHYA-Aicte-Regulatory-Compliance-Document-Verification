import io
import base64
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import cv2
from typing import Dict, Any, Tuple, Optional

class ErrorLevelAnalysisDetector:
    """
    Error Level Analysis (ELA) and Noise Print Detector for detecting digital tampering,
    spliced signatures, altered numbers (e.g. land area or financial amounts),
    and pasted municipal stamps.
    """
    def __init__(self, quality: int = 95, scale: int = 15):
        self.quality = quality
        self.scale = scale

    def analyze_image(self, pil_image: Image.Image) -> Tuple[float, Dict[str, Any], str]:
        """
        Runs ELA on a PIL Image.
        Returns:
            (anomaly_score [0.0 - 1.0], stats_dict, ela_heatmap_base64)
        """
        if pil_image.mode != "RGB":
            pil_image = pil_image.convert("RGB")

        # Step 1: Save temporary image at known JPEG compression quality
        buffer = io.BytesIO()
        pil_image.save(buffer, "JPEG", quality=self.quality)
        buffer.seek(0)
        resaved = Image.open(buffer)

        # Step 2: Compute absolute difference
        ela_im = ImageChops.difference(pil_image, resaved)
        
        # Step 3: Compute extrema and statistical variance
        extrema = ela_im.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        scale_factor = 255.0 / max(max_diff, 1) if max_diff > 0 else 1.0
        
        # Enhance for human viewing
        enhanced = ImageEnhance.Brightness(ela_im).enhance(min(scale_factor, self.scale))
        
        # Step 4: Convert to OpenCV matrix for localized hotspot detection
        ela_cv = np.array(enhanced)
        gray = cv2.cvtColor(ela_cv, cv2.COLOR_RGB2GRAY)
        
        # Statistical distribution
        mean_val = float(np.mean(gray))
        std_val = float(np.std(gray))
        p99_val = float(np.percentile(gray, 99))
        
        # Identify suspicious localized clusters (pixels exceeding 3 standard deviations)
        threshold_val = mean_val + (2.5 * std_val)
        suspicious_mask = (gray > threshold_val).astype(np.uint8) * 255
        
        contours, _ = cv2.findContours(suspicious_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        significant_clusters = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 150]

        # Calculate anomaly score
        # High max difference and significant localized clusters suggest tampering
        cluster_factor = min(len(significant_clusters) / 5.0, 1.0)
        variance_factor = min(std_val / 40.0, 1.0)
        anomaly_score = round(min(0.85 * cluster_factor + 0.15 * variance_factor, 1.0), 3)

        # Colorize ELA for officer dashboard (apply Inferno colormap to highlight hot zones)
        colored_heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        
        # Draw bounding boxes around spliced regions
        for (x, y, w, h) in significant_clusters[:5]:
            cv2.rectangle(colored_heatmap, (x, y), (x + w, y + h), (0, 255, 255), 2)

        # Convert heatmap to base64
        _, encoded_img = cv2.imencode(".png", colored_heatmap)
        heatmap_b64 = f"data:image/png;base64,{base64.b64encode(encoded_img).decode('utf-8')}"

        stats = {
            "max_difference": int(max_diff),
            "mean_error": round(mean_val, 2),
            "std_deviation": round(std_val, 2),
            "p99_error": round(p99_val, 2),
            "tampered_clusters_count": len(significant_clusters),
            "bounding_boxes": [[int(x), int(y), int(w), int(h)] for (x, y, w, h) in significant_clusters[:5]]
        }

        return anomaly_score, stats, heatmap_b64
