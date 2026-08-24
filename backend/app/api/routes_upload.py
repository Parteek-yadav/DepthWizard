# backend/app/api/routes_upload.py
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.app.config import TEMP_DIR
from backend.app.geospatial.geotiff_handler import GeoTIFFHandler

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("")
async def upload_image(file: UploadFile = File(...)):
    """Uploads optical raster or reference DEM and extracts metadata."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename missing")

    ext = Path(file.filename).suffix.lower()
    if ext not in [".tif", ".tiff", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail=f"Unsupported file format: {ext}")

    file_id = str(uuid.uuid4())[:8]
    save_name = f"{file_id}_{file.filename}"
    save_path = TEMP_DIR / save_name

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    metadata = GeoTIFFHandler.inspect_raster(str(save_path))
    return {
        "file_id": file_id,
        "file_path": str(save_path),
        "filename": file.filename,
        "metadata": metadata
    }
