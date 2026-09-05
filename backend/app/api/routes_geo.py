# backend/app/api/routes_geo.py
import json
import logging
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from backend.app.config import OUTPUTS_DIR
from backend.app.geospatial.geo_fetcher import GeoFetcher
from backend.app.processing.pipeline import PipelineOrchestrator
from backend.app.ml.ai_supervisor import ReconstructionSupervisor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/geo", tags=["Geographic Discovery & Selection"])

class SelectAreaRequest(BaseModel):
    lat: float = Field(..., ge=-90.0, le=90.0, description="Center latitude in degrees")
    lon: float = Field(..., ge=-180.0, le=180.0, description="Center longitude in degrees")
    radius_meters: float = Field(default=500.0, ge=100.0, le=10000.0, description="Selection radius in meters")
    name: Optional[str] = Field(default=None, description="Optional location / region name")

class ProcessSelectedRequest(BaseModel):
    lat: float
    lon: float
    radius_meters: float = 500.0
    name: Optional[str] = None
    mesh_resolution: int = 128
    height_exaggeration: float = 1.0

class ProcessSelectedRectRequest(BaseModel):
    min_lon: float = Field(..., ge=-180.0, le=180.0)
    min_lat: float = Field(..., ge=-90.0, le=90.0)
    max_lon: float = Field(..., ge=-180.0, le=180.0)
    max_lat: float = Field(..., ge=-90.0, le=90.0)
    name: Optional[str] = None
    mesh_resolution: int = 128
    height_exaggeration: float = 1.0

@router.get("/search")
async def search_locations(q: str = Query(default="", description="Search query for location / landmark")):
    """Searches global gazetteer and returns matched locations with coordinates."""
    results = GeoFetcher.search_locations(q)
    return {"query": q, "count": len(results), "results": results}

@router.post("/select_area")
async def select_area(payload: SelectAreaRequest):
    """
    Defines the selected geographic region, extracts bounds, CRS,
    generates optical/DEM datasets, and compiles 3D building models.
    """
    try:
        area_info = GeoFetcher.generate_area_dataset(
            lat=payload.lat,
            lon=payload.lon,
            radius_meters=payload.radius_meters,
            area_name=payload.name
        )
        return {"status": "success", "area": area_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to define geographic area: {str(e)}")

@router.post("/process_selected")
async def process_selected_area(payload: ProcessSelectedRequest):
    """
    End-to-End Execution: Takes selected geographic area, generates satellite raster & reference DEM,
    runs DepthWizard monocular depth + Huber elevation calibration, and attaches 3D buildings.
    """
    try:
        area_info = GeoFetcher.generate_area_dataset(
            lat=payload.lat,
            lon=payload.lon,
            radius_meters=payload.radius_meters,
            area_name=payload.name,
            mesh_resolution=payload.mesh_resolution
        )

        pipeline_result = PipelineOrchestrator.process(
            image_path=area_info["image_path"],
            dem_path=area_info["dem_path"],
            mesh_resolution=payload.mesh_resolution,
            height_exaggeration=payload.height_exaggeration,
            spatial_bounds_meters=area_info["spatial_bounds_meters"],
            texture_path=area_info.get("texture_path")
        )

        # AI Supervisor analysis
        supervisor_eval = ReconstructionSupervisor.analyze_reconstruction_context(
            scene_type="Georeferenced Satellite Selection",
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
            "radius_meters": area_info["radius_meters"],
            "approx_area_km2": area_info.get("approx_area_km2", 1.0),
            "projected_crs": area_info["crs"],
            "geographic_crs": area_info["geographic_crs"],
            "building_count": area_info["building_count"]
        }
        pipeline_result["buildings"] = area_info["buildings"]
        pipeline_result["supervisor_decision"] = supervisor_eval
        pipeline_result["data_provenance"] = {
            "terrain_source": "NASA SRTM GL1 30m / Copernicus DEM COP30",
            "imagery_source": "Esri World Imagery & OpenStreetMap",
            "building_source": "OpenStreetMap Overpass API Vector Footprints",
            "depth_backbone": "Depth Anything V2 (ViT-Small)",
            "calibration_method": "Robust Huber M-Estimation Regression"
        }

        return pipeline_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process selected geographic area: {str(e)}")

@router.post("/process_selected_rect")
async def process_selected_rect_area(payload: ProcessSelectedRectRequest):
    """
    End-to-End Execution for Paint-Style Rectangle Selection:
    Ingests exact bounding box (min_lon, min_lat, max_lon, max_lat),
    generates georeferenced raster & DEM matching physical dimensions,
    and returns continuous 3D terrain surface with real metric scale.
    """
    try:
        # Check pre-warmed disk cache for curated demo locations
        from backend.app.api.routes_demo import CURATED_DEMO_LOCATIONS
        for loc in CURATED_DEMO_LOCATIONS:
            if (
                abs(payload.min_lon - loc["min_lon"]) < 0.003
                and abs(payload.min_lat - loc["min_lat"]) < 0.003
                and abs(payload.max_lon - loc["max_lon"]) < 0.003
                and abs(payload.max_lat - loc["max_lat"]) < 0.003
            ):
                disk_report = OUTPUTS_DIR / loc["id"] / "report.json"
                if disk_report.exists():
                    logger.info("Serving pre-warmed disk cache for %s (%s)", loc["name"], loc["id"])
                    with open(disk_report, "r", encoding="utf-8") as f:
                        return json.load(f)

        area_info = GeoFetcher.generate_rect_area_dataset(
            min_lon=payload.min_lon,
            min_lat=payload.min_lat,
            max_lon=payload.max_lon,
            max_lat=payload.max_lat,
            area_name=payload.name,
            mesh_resolution=payload.mesh_resolution
        )

        pipeline_result = PipelineOrchestrator.process(
            image_path=area_info["image_path"],
            dem_path=area_info["dem_path"],
            mesh_resolution=payload.mesh_resolution,
            height_exaggeration=payload.height_exaggeration,
            spatial_bounds_meters=area_info["spatial_bounds_meters"],
            texture_path=area_info.get("texture_path")
        )

        # AI Supervisor analysis
        supervisor_eval = ReconstructionSupervisor.analyze_reconstruction_context(
            scene_type="Paint-Style Geographic Rectangle Selection",
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
            "building_source": "OpenStreetMap Overpass API Vector Footprints",
            "depth_backbone": "Depth Anything V2 (ViT-Small)",
            "calibration_method": "Robust Huber M-Estimation Regression"
        }

        return pipeline_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process rectangular area: {str(e)}")
