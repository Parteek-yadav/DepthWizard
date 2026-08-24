# backend/app/api/routes_demo.py
from pathlib import Path
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from backend.app.config import DEMO_DATA_DIR

router = APIRouter(prefix="/api/demo", tags=["Demo"])

@router.get("/datasets")
async def list_demo_datasets():
    """Lists available bundled datasets for zero-config offline demonstration."""
    return {
        "datasets": [
            {
                "id": "himalaya_mountain",
                "name": "Himalayan Ridge & Valley (Georeferenced GeoTIFF)",
                "description": "Satellite optical RGB tile (EPSG:32643) with matched SRTM 30m reference DEM. Demonstrates absolute metric DSM calibration.",
                "image_path": str(DEMO_DATA_DIR / "himalaya_optical.tif"),
                "dem_path": str(DEMO_DATA_DIR / "himalaya_srtm_dem.tif"),
                "is_georeferenced": True,
                "expected_crs": "EPSG:32643",
                "elevation_range": "850m - 2450m"
            },
            {
                "id": "urban_infrastructure",
                "name": "Urban Infrastructure & High-Rise (GCP Mode)",
                "description": "Optical imagery with 4 Ground Control Points on building rooftops and ground base for structural height measurement.",
                "image_path": str(DEMO_DATA_DIR / "urban_optical.tif"),
                "is_georeferenced": True,
                "expected_crs": "EPSG:32643",
                "gcps": [
                    {"id": "GCP-1", "pixel_x": 120.0, "pixel_y": 140.0, "elevation_meters": 185.0, "description": "Tower A Apex"},
                    {"id": "GCP-2", "pixel_x": 380.0, "pixel_y": 210.0, "elevation_meters": 230.0, "description": "Tower B Rooftop"},
                    {"id": "GCP-3", "pixel_x": 250.0, "pixel_y": 420.0, "elevation_meters": 75.0, "description": "Plaza Ground"},
                    {"id": "GCP-4", "pixel_x": 450.0, "pixel_y": 460.0, "elevation_meters": 68.0, "description": "Road Intersection"}
                ]
            },
            {
                "id": "drone_aerial_coastal",
                "name": "Drone Aerial Coastal Snapshot (Non-Georeferenced)",
                "description": "Standard optical RGB snapshot (PNG). Demonstrates zero-shot relative depth and rDSM 3D flythrough without geospatial tags.",
                "image_path": str(DEMO_DATA_DIR / "drone_coastal.png"),
                "is_georeferenced": False
            }
        ]
    }
