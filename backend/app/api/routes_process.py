# backend/app/api/routes_process.py
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
from backend.app.processing.pipeline import PipelineOrchestrator

router = APIRouter(prefix="/api/process", tags=["Processing"])

class ProcessRequest(BaseModel):
    image_path: str
    dem_path: Optional[str] = None
    gcps: Optional[List[Dict[str, Any]]] = None
    mesh_resolution: Optional[int] = 128
    height_exaggeration: Optional[float] = 1.0

@router.post("")
async def run_processing(req: ProcessRequest):
    """Executes full monocular depth, calibration, and 3D terrain pipeline."""
    try:
        result = PipelineOrchestrator.process(
            image_path=req.image_path,
            dem_path=req.dem_path,
            gcps=req.gcps,
            mesh_resolution=req.mesh_resolution or 128,
            height_exaggeration=req.height_exaggeration or 1.0
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
