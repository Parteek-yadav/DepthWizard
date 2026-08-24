from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from pydantic import BaseModel

class GroundControlPoint(BaseModel):
    id: str
    pixel_x: float
    pixel_y: float
    elevation_meters: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = "GCP Reference Point"

class GCPManager:
    """Manages Ground Control Points (GCPs) and extracts pairing with relative depth predictions."""

    @staticmethod
    def sample_gcp_pairs(gcps: List[GroundControlPoint], relative_depth: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extracts (D_rel, Z_true) pairs for all valid GCP coordinates.
        Returns:
            d_samples: 1D np.ndarray
            z_samples: 1D np.ndarray
        """
        H, W = relative_depth.shape
        d_vals = []
        z_vals = []

        for gcp in gcps:
            px = int(round(gcp.pixel_x))
            py = int(round(gcp.pixel_y))
            if 0 <= px < W and 0 <= py < H:
                d_val = relative_depth[py, px]
                if not np.isnan(d_val):
                    d_vals.append(float(d_val))
                    z_vals.append(float(gcp.elevation_meters))

        return np.array(d_vals, dtype=np.float64), np.array(z_vals, dtype=np.float64)
