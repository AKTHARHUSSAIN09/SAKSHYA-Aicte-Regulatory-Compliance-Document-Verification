from typing import Dict, Any, Optional, Tuple
from PIL import Image, ExifTags
import math
from pydantic import BaseModel

class GeoVerificationResult(BaseModel):
    has_exif: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capture_time: Optional[str] = None
    camera_model: Optional[str] = None
    distance_to_land_centroid_km: Optional[float] = None
    is_within_campus_boundary: bool = False
    status: str = "PENDING"
    notes: str = ""

class InfrastructureGeoVerifier:
    """
    Module 7: Infrastructure Compliance Assistance.
    Extracts EXIF metadata from campus photographs and videos (laboratories, libraries, classrooms)
    and verifies that the GPS coordinates match the registered institutional land coordinates.
    """
    def __init__(self, tolerance_km: float = 0.5):
        self.tolerance_km = tolerance_km  # 500 meters tolerance

    def extract_exif_gps(self, pil_image: Image.Image) -> Tuple[Optional[float], Optional[float], Optional[str], Optional[str]]:
        try:
            exif_raw = pil_image._getexif()
            if not exif_raw:
                return None, None, None, None

            exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_raw.items()}
            gps_info = exif.get("GPSInfo")
            capture_time = exif.get("DateTimeOriginal") or exif.get("DateTime")
            camera_model = f"{exif.get('Make', '')} {exif.get('Model', '')}".strip() or None

            if not gps_info:
                return None, None, capture_time, camera_model

            lat = self._convert_to_degrees(gps_info.get(2))
            if gps_info.get(1) == "S":
                lat = -lat

            lon = self._convert_to_degrees(gps_info.get(4))
            if gps_info.get(3) == "W":
                lon = -lon

            return lat, lon, capture_time, camera_model
        except Exception:
            return None, None, None, None

    def _convert_to_degrees(self, value):
        if not value:
            return 0.0
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Computes Great Circle distance between two GPS coordinates in kilometers."""
        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2.0) ** 2
            + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def verify_campus_photo(
        self,
        pil_image: Image.Image,
        campus_target_lat: float,
        campus_target_lon: float
    ) -> GeoVerificationResult:
        lat, lon, capture_time, camera_model = self.extract_exif_gps(pil_image)
        if lat is None or lon is None:
            return GeoVerificationResult(
                has_exif=False,
                capture_time=capture_time,
                camera_model=camera_model,
                status="EXIF_GPS_MISSING",
                notes="Photograph does not contain embedded GPS coordinates. Requires manual inspection or geotagged re-upload."
            )

        dist = self.haversine_distance(lat, lon, campus_target_lat, campus_target_lon)
        is_valid = dist <= self.tolerance_km

        if is_valid:
            return GeoVerificationResult(
                has_exif=True,
                latitude=round(lat, 6),
                longitude=round(lon, 6),
                capture_time=capture_time,
                camera_model=camera_model,
                distance_to_land_centroid_km=round(dist, 3),
                is_within_campus_boundary=True,
                status="VERIFIED_ON_CAMPUS",
                notes=f"Photograph verified within campus perimeter ({round(dist * 1000, 1)} meters from land deed centroid)."
            )
        else:
            return GeoVerificationResult(
                has_exif=True,
                latitude=round(lat, 6),
                longitude=round(lon, 6),
                capture_time=capture_time,
                camera_model=camera_model,
                distance_to_land_centroid_km=round(dist, 3),
                is_within_campus_boundary=False,
                status="GEO_LOCATION_MISMATCH",
                notes=f"GPS anomaly: Photograph taken {round(dist, 2)} km away from the registered institutional land coordinates."
            )
