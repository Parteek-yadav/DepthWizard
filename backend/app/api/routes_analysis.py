# backend/app/api/routes_analysis.py
import math
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import numpy as np

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

class ProfileRequest(BaseModel):
    task_id: str
    point_a: List[float] # [x1, y1] normalized [0, 1]
    point_b: List[float] # [x2, y2] normalized [0, 1]
    num_samples: Optional[int] = 50

class MeasureRequest(BaseModel):
    task_id: str
    point_a: List[float] # [x1, y1]
    point_b: List[float] # [x2, y2]
    z1: float
    z2: float
    gsd_meters: Optional[float] = 1.0

@router.post("/profile")
async def get_elevation_profile(req: ProfileRequest):
    """Samples elevation along a transect line from point A to point B."""
    # Generate interpolated profile
    x1, y1 = req.point_a
    x2, y2 = req.point_b
    n = req.num_samples or 50

    xs = np.linspace(x1, x2, n)
    ys = np.linspace(y1, y2, n)

    # Return profile points
    profile = []
    for i in range(n):
        profile.append({
            "distance_ratio": round(float(i / (n - 1)), 3),
            "x": round(float(xs[i]), 4),
            "y": round(float(ys[i]), 4),
            "elevation": 0.0 # Will be populated dynamically on frontend or from cached grid
        })

    return {"profile": profile}

@router.post("/measure")
async def calculate_measurement(req: MeasureRequest):
    """Calculates physical 3D distance, delta Z, and slope grade/angle."""
    dx_norm = req.point_b[0] - req.point_a[0]
    dy_norm = req.point_b[1] - req.point_a[1]
    dz = req.z2 - req.z1

    # Approximate ground horizontal distance
    gsd = req.gsd_meters if req.gsd_meters else 1.0
    # Normalized [0, 1] distance in pixels scaled by GSD
    pixel_dist = math.sqrt(dx_norm**2 + dy_norm**2) * 512.0
    horiz_dist_m = pixel_dist * gsd

    slope_pct = (abs(dz) / (horiz_dist_m + 1e-6)) * 100.0
    slope_angle_deg = math.degrees(math.atan2(abs(dz), horiz_dist_m + 1e-6))
    dist_3d_m = math.sqrt(horiz_dist_m**2 + dz**2)

    return {
        "delta_z": round(dz, 2),
        "horizontal_distance_m": round(horiz_dist_m, 2),
        "distance_3d_m": round(dist_3d_m, 2),
        "slope_percentage": round(slope_pct, 2),
        "slope_angle_deg": round(slope_angle_deg, 2)
    }
