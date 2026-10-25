from __future__ import annotations
import io
import shutil
from typing import Any
import cv2
import numpy as np
from PIL import Image

def inspect_signature_and_qr(file_name: str, content: bytes) -> dict[str, Any]:
    is_pdf = file_name.lower().endswith(".pdf") or content[:4] == b"%PDF"
    signature_present = is_pdf and b"/ByteRange" in content and b"/Contents" in content
    qr_payloads: list[str] = []
    qr_status = "NOT_FOUND"
    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
        value, _, _ = cv2.QRCodeDetector().detectAndDecode(np.array(image))
        if value:
            qr_payloads.append(value)
            qr_status = "DECODED"
    except Exception:
        qr_status = "MANUAL_REVIEW_REQUIRED" if is_pdf else "NOT_FOUND"
    return {"digital_signature": {"status": "PRESENT_UNVERIFIED" if signature_present else "NOT_PRESENT_OR_UNSUPPORTED",
                                  "manual_review_required": signature_present},
            "qr_code": {"status": qr_status, "payloads": qr_payloads,
                        "manual_review_required": qr_status == "MANUAL_REVIEW_REQUIRED"}}

def ocr_image(content: bytes) -> dict[str, Any]:
    """OCR scanned images when native Tesseract is available; never fabricate text."""
    if not shutil.which("tesseract"):
        return {"status": "MANUAL_REVIEW_REQUIRED", "reason": "Tesseract OCR binary is not installed", "text": ""}
    try:
        import pytesseract
        image = Image.open(io.BytesIO(content)).convert("RGB")
        text = pytesseract.image_to_string(image)
        return {"status": "EXTRACTED", "text": text, "raw_text_length": len(text)}
    except Exception as exc:
        return {"status": "MANUAL_REVIEW_REQUIRED", "reason": str(exc), "text": ""}

def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None
