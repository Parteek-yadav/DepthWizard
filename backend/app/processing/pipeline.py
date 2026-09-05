# backend/app/processing/pipeline.py
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
from PIL import Image

from backend.app.config import OUTPUTS_DIR
from backend.app.geospatial.geotiff_handler import GeoTIFFHandler
from backend.app.geospatial.dem_aligner import DEMAligner
from backend.app.geospatial.gcp_manager import GCPManager, GroundControlPoint
from backend.app.geospatial.calibrator import ElevationCalibrator
from backend.app.ml.model_manager import ModelManager
from backend.app.ml.colormap_utils import save_colormap_image
from backend.app.processing.mesh_generator import MeshGenerator
from backend.app.processing.exporter import ResultExporter

logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    """End-to-End Orchestrator for DepthWizard Single-View Height Estimation."""

    @classmethod
    def process(
        cls,
        image_path: str,
        dem_path: Optional[str] = None,
        gcps: Optional[List[Dict[str, Any]]] = None,
        mesh_resolution: int = 128,
        height_exaggeration: float = 1.0,
        task_id: Optional[str] = None,
        spatial_bounds_meters: Optional[Tuple[float, float, float, float]] = None,
        texture_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end processing pipeline:
        1. Reads and validates optical image.
        2. Infers monocular relative depth via configured Depth Anything V2 model.
        3. Calibrates relative depth against reference DEM or GCPs.
        4. Generates continuous 3D triangle mesh with analytical surface normals.
        5. Exports analysis report, GeoTIFF DSM, OBJ mesh, and previews.
        """
        if task_id is None:
            task_id = f"task_{uuid.uuid4().hex[:8]}"

        task_dir = OUTPUTS_DIR / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # 1. Load optical image and extract spatial metadata
        rgb_img, spatial_meta = GeoTIFFHandler.read_rgb(image_path)
        H, W, _ = rgb_img.shape

        # Save copy of source RGB texture for Three.js (prefer high-fidelity texture if available)
        rgb_texture_path = task_dir / "texture.png"
        if texture_path and Path(texture_path).exists():
            try:
                tex_img, _ = GeoTIFFHandler.read_rgb(texture_path)
                Image.fromarray(tex_img).save(str(rgb_texture_path), format="PNG")
            except Exception as e:
                logger.warning("Could not read custom texture_path %s: %s. Falling back to optical image.", texture_path, e)
                Image.fromarray(rgb_img).save(str(rgb_texture_path), format="PNG")
        else:
            Image.fromarray(rgb_img).save(str(rgb_texture_path), format="PNG")

        # 2. Monocular depth inference
        depth_model = ModelManager.get_instance().get_depth_model()
        relative_depth = depth_model.predict(rgb_img)

        # Save relative depth colorized preview
        rel_depth_png = task_dir / "relative_depth.png"
        save_colormap_image(relative_depth, str(rel_depth_png), colormap_name="turbo")

        is_georeferenced = spatial_meta.get("is_georeferenced", False)
        is_absolute = False
        calibration_metrics = None
        elevation_data = None
        elevation_unit = "relative_units"

        # 3. Calibration logic
        if is_georeferenced and dem_path and Path(dem_path).exists():
            # Align DEM
            aligned_dem = DEMAligner.load_and_align_dem(dem_path, target_shape=(H, W))
            elevation_data, calibration_metrics = ElevationCalibrator.calibrate_from_dem(
                relative_depth=relative_depth,
                reference_dem=aligned_dem
            )
            is_absolute = True
            elevation_unit = "meters"
        elif is_georeferenced and gcps and len(gcps) >= 2:
            # GCP Calibration
            gcp_objs = [GroundControlPoint(**g) for g in gcps]
            d_samples, z_samples = GCPManager.sample_gcp_pairs(gcp_objs, relative_depth)
            elevation_data, calibration_metrics = ElevationCalibrator.calibrate_from_gcps(
                relative_depth, d_samples, z_samples
            )
            is_absolute = True
            elevation_unit = "meters"
        else:
            # Mode 1: Non-georeferenced Relative DSM
            elevation_data = relative_depth.copy()
            is_absolute = False
            elevation_unit = "relative_units"

        # Save DSM colorized preview
        dsm_png = task_dir / "dsm_preview.png"
        save_colormap_image(
            (elevation_data - np.nanmin(elevation_data)) / (np.nanmax(elevation_data) - np.nanmin(elevation_data) + 1e-8),
            str(dsm_png),
            colormap_name="terrain" if is_absolute else "turbo"
        )

        # Export GeoTIFF DSM if georeferenced
        geotiff_dsm_filename = None
        if is_georeferenced:
            geotiff_path = task_dir / "dsm_metric.tif"
            if ResultExporter.export_geotiff_dsm(elevation_data, str(geotiff_path), spatial_meta):
                geotiff_dsm_filename = f"/outputs/{task_id}/dsm_metric.tif"

        # 4. Generate 3D Terrain Mesh
        mesh_data = MeshGenerator.generate_terrain_mesh(
            elevation_2d=elevation_data,
            target_grid_size=mesh_resolution,
            height_exaggeration=height_exaggeration,
            spatial_bounds_meters=spatial_bounds_meters
        )

        # Export OBJ
        obj_path = task_dir / "terrain.obj"
        MeshGenerator.export_obj(mesh_data, str(obj_path))

        # 5. Compute Hypsometric histogram
        hist_counts, bin_edges = np.histogram(elevation_data[~np.isnan(elevation_data)], bins=20)
        histogram_data = [
            {"bin_start": round(float(bin_edges[i]), 2), "bin_end": round(float(bin_edges[i+1]), 2), "count": int(hist_counts[i])}
            for i in range(len(hist_counts))
        ]

        summary_stats = {
            "min_elevation": round(float(np.nanmin(elevation_data)), 2),
            "max_elevation": round(float(np.nanmax(elevation_data)), 2),
            "mean_elevation": round(float(np.nanmean(elevation_data)), 2),
            "std_elevation": round(float(np.nanstd(elevation_data)), 2),
            "elevation_unit": elevation_unit,
            "dimensions": {"width": W, "height": H},
            "is_georeferenced": is_georeferenced,
            "is_absolute": is_absolute
        }

        # Save full analysis report
        report_payload = {
            "task_id": task_id,
            "spatial_metadata": spatial_meta,
            "model_metadata": depth_model.get_metadata(),
            "calibration": calibration_metrics,
            "statistics": summary_stats,
            "histogram": histogram_data
        }
        ResultExporter.export_analysis_report(report_payload, str(task_dir / "report.json"))

        return {
            "task_id": task_id,
            "status": "success",
            "is_georeferenced": is_georeferenced,
            "is_absolute": is_absolute,
            "elevation_unit": elevation_unit,
            "spatial_metadata": spatial_meta,
            "model_metadata": depth_model.get_metadata(),
            "calibration_metrics": calibration_metrics,
            "statistics": summary_stats,
            "histogram": histogram_data,
            "mesh": mesh_data,
            "urls": {
                "texture": f"/outputs/{task_id}/texture.png",
                "relative_depth": f"/outputs/{task_id}/relative_depth.png",
                "dsm_preview": f"/outputs/{task_id}/dsm_preview.png",
                "geotiff_dsm": geotiff_dsm_filename,
                "obj_mesh": f"/outputs/{task_id}/terrain.obj",
                "report_json": f"/outputs/{task_id}/report.json"
            }
        }
