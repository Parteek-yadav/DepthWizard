# backend/tests/test_end_to_end.py
import pytest
from backend.app.processing.pipeline import PipelineOrchestrator
from backend.app.config import DEMO_DATA_DIR

def test_pipeline_mode_1_non_georeferenced():
    img_path = DEMO_DATA_DIR / "drone_coastal.png"
    result = PipelineOrchestrator.process(
        image_path=str(img_path),
        mesh_resolution=64
    )

    assert result["status"] == "success"
    assert result["is_georeferenced"] is False
    assert result["is_absolute"] is False
    assert result["elevation_unit"] == "relative_units"
    assert "urls" in result
    assert result["urls"]["texture"] is not None
    assert result["urls"]["relative_depth"] is not None
    assert result["urls"]["obj_mesh"] is not None

def test_pipeline_mode_2_georeferenced_with_dem():
    img_path = DEMO_DATA_DIR / "himalaya_optical.tif"
    dem_path = DEMO_DATA_DIR / "himalaya_srtm_dem.tif"

    result = PipelineOrchestrator.process(
        image_path=str(img_path),
        dem_path=str(dem_path),
        mesh_resolution=64
    )

    assert result["status"] == "success"
    assert result["is_georeferenced"] is True
    assert result["is_absolute"] is True
    assert result["elevation_unit"] == "meters"
    assert result["calibration_metrics"] is not None
    assert result["calibration_metrics"]["r2_score"] is not None
    assert result["calibration_metrics"]["rmse_meters"] is not None
    assert result["urls"]["geotiff_dsm"] is not None
