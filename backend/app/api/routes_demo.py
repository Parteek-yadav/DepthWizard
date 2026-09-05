# backend/app/api/routes_demo.py
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from backend.app.config import DEMO_DATA_DIR, OUTPUTS_DIR, DEMO_MODE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/demo", tags=["Demo"])

# Fixed reserved curated locations for instant, zero-latency Demo Mode
CURATED_DEMO_LOCATIONS: List[Dict[str, Any]] = [
    {
        "id": "demo_jaipur",
        "name": "Jaipur City Palace & Hawa Mahal",
        "min_lon": 75.820,
        "min_lat": 26.918,
        "max_lon": 75.832,
        "max_lat": 26.928,
        "mesh_resolution": 128,
        "height_exaggeration": 1.0
    },
    {
        "id": "demo_taj_mahal",
        "name": "Taj Mahal & Yamuna Riverfront",
        "min_lon": 78.036,
        "min_lat": 27.170,
        "max_lon": 78.048,
        "max_lat": 27.180,
        "mesh_resolution": 128,
        "height_exaggeration": 1.0
    },
    {
        "id": "demo_india_gate",
        "name": "India Gate & Central Vista",
        "min_lon": 77.223,
        "min_lat": 28.607,
        "max_lon": 77.235,
        "max_lat": 28.618,
        "mesh_resolution": 128,
        "height_exaggeration": 1.0
    },
    {
        "id": "demo_istrac",
        "name": "ISRO Telemetry & Tracking Command Network (ISTRAC)",
        "min_lon": 77.558,
        "min_lat": 13.028,
        "max_lon": 77.570,
        "max_lat": 13.039,
        "mesh_resolution": 128,
        "height_exaggeration": 1.0
    }
]


def prewarm_demo_cache() -> List[str]:
    """
    Pre-warms and caches full pipeline results (mesh, texture, DSM, report.json)
    to disk under fixed reserved task_ids in OUTPUTS_DIR.
    Logs progress per location so slow startup is distinguishable from hung startup.
    """
    from backend.app.geospatial.geo_fetcher import GeoFetcher
    from backend.app.processing.pipeline import PipelineOrchestrator
    from backend.app.ml.ai_supervisor import ReconstructionSupervisor

    total = len(CURATED_DEMO_LOCATIONS)
    prewarmed_ids = []

    for idx, loc in enumerate(CURATED_DEMO_LOCATIONS, 1):
        task_id = loc["id"]
        loc_name = loc["name"]
        logger.info("Pre-warming %d/%d: %s...", idx, total, loc_name)

        task_dir = OUTPUTS_DIR / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        report_file = task_dir / "report.json"

        # Check if already cached on disk
        if report_file.exists():
            logger.info("Location %d/%d: %s already cached on disk at %s.", idx, total, loc_name, task_dir)
            prewarmed_ids.append(task_id)
            continue

        try:
            area_info = GeoFetcher.generate_rect_area_dataset(
                min_lon=loc["min_lon"],
                min_lat=loc["min_lat"],
                max_lon=loc["max_lon"],
                max_lat=loc["max_lat"],
                area_name=loc["name"],
                mesh_resolution=loc["mesh_resolution"]
            )

            pipeline_result = PipelineOrchestrator.process(
                image_path=area_info["image_path"],
                dem_path=area_info["dem_path"],
                mesh_resolution=loc["mesh_resolution"],
                height_exaggeration=loc["height_exaggeration"],
                spatial_bounds_meters=area_info["spatial_bounds_meters"],
                task_id=task_id,
                texture_path=area_info.get("texture_path")
            )

            supervisor_eval = ReconstructionSupervisor.analyze_reconstruction_context(
                scene_type="Pre-warmed Curated Landmark Demo",
                geographic_bounds=area_info["bounds"],
                dimensions_meters=area_info["dimensions_meters"],
                terrain_stats=pipeline_result["statistics"],
                building_count=area_info["building_count"],
                has_dem=True
            )

            pipeline_result["geographic_context"] = {
                "name": area_info["name"],
                "center": area_info["center"],
                "bounds": area_info["bounds"],
                "dimensions_meters": area_info["dimensions_meters"],
                "approx_area_km2": area_info["approx_area_km2"],
                "spatial_bounds_meters": area_info["spatial_bounds_meters"],
                "projected_crs": area_info["crs"],
                "geographic_crs": area_info["geographic_crs"],
                "building_count": area_info["building_count"]
            }
            pipeline_result["buildings"] = area_info["buildings"]
            pipeline_result["supervisor_decision"] = supervisor_eval
            pipeline_result["data_provenance"] = {
                "terrain_source": "NASA SRTM GL1 30m / Copernicus DEM COP30",
                "imagery_source": "Esri World Imagery & OpenStreetMap",
                "building_source": "OpenStreetMap Overpass API Vector Footprints (Curated Offline Vector Landmark)",
                "depth_backbone": "Depth Anything V2 (ViT-Small)",
                "calibration_method": "Robust Huber M-Estimation Regression",
                "demo_mode": True
            }

            # Save full report.json and mesh.json for instant reload
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(pipeline_result, f, indent=2)
            with open(task_dir / "mesh.json", "w", encoding="utf-8") as f:
                json.dump(pipeline_result["mesh"], f)

            logger.info("Pre-warming %d/%d: %s COMPLETE -> %s", idx, total, loc_name, task_id)
            prewarmed_ids.append(task_id)
        except Exception as e:
            logger.error("Pre-warming %d/%d: %s FAILED: %s", idx, total, loc_name, str(e), exc_info=True)

    return prewarmed_ids


@router.get("/scripted_run")
@router.post("/scripted_run")
async def scripted_demo_run():
    """Triggers pre-warming of curated demo locations and caches them to disk under reserved task_ids."""
    cached_ids = prewarm_demo_cache()
    return {
        "status": "success",
        "demo_mode": DEMO_MODE,
        "prewarmed_locations": cached_ids,
        "message": f"Successfully pre-warmed and cached {len(cached_ids)} demo locations under reserved task_ids."
    }


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
