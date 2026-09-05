# backend/app/api/routes_img2d3d.py
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
from PIL import Image
from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pydantic import BaseModel, Field

from backend.app.config import TEMP_DIR, OUTPUTS_DIR
from backend.app.ml.model_manager import ModelManager
from backend.app.ml.colormap_utils import save_colormap_image
from backend.app.processing.mesh_generator import MeshGenerator
from backend.app.ml.ai_supervisor import ReconstructionSupervisor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/img2d3d", tags=["2D to 3D Conversion"])

class ConvertParams(BaseModel):
    image_path: str
    depth_strength: float = Field(default=1.5, ge=0.1, le=5.0)
    mesh_resolution: int = Field(default=128, ge=32, le=512)
    smoothing: bool = Field(default=True)

@router.post("/convert")
async def convert_2d_to_3d(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None),
    depth_strength: float = Form(1.5),
    mesh_resolution: int = Form(128)
):
    """
    Converts ANY ordinary 2D photograph / image (PNG/JPG) into an interactive 3D terrain/mesh:
    1. Ingests photo (no GPS/DEM required)
    2. Runs Depth Anything V2 monocular depth inference
    3. Normalizes depth into height field
    4. Evaluates depth quality and runs AI supervision
    5. Generates triangulated 3D TIN mesh with smooth normals & UV coordinates
    6. Maps the original image directly as high-resolution PBR surface texture
    7. Serializes Wavefront OBJ and returns render payload
    """
    task_id = str(uuid.uuid4())[:8]
    task_dir = OUTPUTS_DIR / f"img3d_{task_id}"
    task_dir.mkdir(parents=True, exist_ok=True)

    input_img_path = None

    if file and file.filename:
        ext = Path(file.filename).suffix.lower()
        if ext not in [".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"]:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {ext}")
        saved_file = task_dir / f"input_photo{ext}"
        with open(saved_file, "wb") as buf:
            buf.write(await file.read())
        input_img_path = saved_file
    elif image_path and Path(image_path).exists():
        input_img_path = Path(image_path)
    else:
        raise HTTPException(status_code=400, detail="Must provide either an uploaded file or valid image_path")

    try:
        # 1. Load image
        pil_img = Image.open(str(input_img_path)).convert("RGB")
        rgb_arr = np.array(pil_img)
        H, W, _ = rgb_arr.shape

        # Save texture
        texture_path = task_dir / "texture.png"
        pil_img.save(str(texture_path), format="PNG")

        # 2. Predict monocular depth via Depth Anything V2
        depth_model = ModelManager.get_instance().get_depth_model()
        depth_rel = depth_model.predict(rgb_arr)

        # Depth Quality Assessment
        depth_quality = ReconstructionSupervisor.assess_depth_quality(depth_rel)

        # AI Supervisor analysis
        supervisor_eval = ReconstructionSupervisor.analyze_reconstruction_context(
            scene_type="2D Photo Monocular Depth Reconstruction",
            geographic_bounds=None,
            dimensions_meters={"width": float(W), "height": float(H)},
            terrain_stats={"min_meters": depth_quality["min"], "max_meters": depth_quality["max"]},
            depth_stats=depth_quality,
            building_count=0,
            has_dem=False
        )

        # Save colorized depth preview
        depth_png = task_dir / "depth_map.png"
        save_colormap_image(depth_rel, str(depth_png), colormap_name="turbo")

        # 3. Generate 3D height-field mesh
        mesh_data = MeshGenerator.generate_terrain_mesh(
            elevation_2d=depth_rel,
            target_grid_size=mesh_resolution,
            height_exaggeration=depth_strength
        )

        # Export Wavefront OBJ
        obj_path = task_dir / "model_3d.obj"
        MeshGenerator.export_obj(mesh_data, str(obj_path))

        # Compute Depth Distribution Histogram
        hist_counts, bin_edges = np.histogram(depth_rel, bins=20)
        histogram_data = [
            {"bin_start": round(float(bin_edges[i]), 3), "bin_end": round(float(bin_edges[i+1]), 3), "count": int(hist_counts[i])}
            for i in range(len(hist_counts))
        ]

        summary_stats = {
            "min_elevation": round(float(np.min(depth_rel)), 3),
            "max_elevation": round(float(np.max(depth_rel)), 3),
            "mean_elevation": round(float(np.mean(depth_rel)), 3),
            "std_elevation": round(float(np.std(depth_rel)), 3),
            "elevation_unit": "relative",
            "dimensions": {"width": W, "height": H},
            "is_georeferenced": False,
            "is_absolute": False
        }

        source_name = file.filename if file and file.filename else (Path(image_path).name if image_path else "2D Image")

        return {
            "task_id": f"img3d_{task_id}",
            "status": "success",
            "feature": "2D Image to 3D Reconstruction",
            "methodology": "Depth Anything V2 Monocular Depth Field Normalization",
            "type": "Monocular depth-derived 3D (Non-metric relative height field)",
            "dimensions": {"width": W, "height": H},
            "depth_strength": depth_strength,
            "mesh_resolution": mesh_resolution,
            "model_metadata": depth_model.get_metadata(),
            "depth_quality": depth_quality,
            "supervisor_decision": supervisor_eval,
            "mesh": mesh_data,
            "statistics": summary_stats,
            "histogram": histogram_data,
            "buildings": [],
            "geographic_context": {
                "name": f"Photo: {source_name}",
                "projected_crs": "Relative / Single-View Coordinate Frame",
                "dimensions_meters": {"width": W, "height": H},
                "approx_area_km2": round((W * H) / 1000000.0, 3)
            },
            "urls": {
                "texture": f"/outputs/img3d_{task_id}/texture.png",
                "depth_map": f"/outputs/img3d_{task_id}/depth_map.png",
                "relative_depth": f"/outputs/img3d_{task_id}/depth_map.png",
                "dsm_preview": f"/outputs/img3d_{task_id}/depth_map.png",
                "obj_mesh": f"/outputs/img3d_{task_id}/model_3d.obj"
            }
        }
    except Exception as e:
        logger.exception("Error converting 2D image to 3D")
        raise HTTPException(status_code=500, detail=f"2D to 3D conversion failed: {str(e)}")
