# backend/tests/test_geotiff_crs.py
import pytest
from pathlib import Path
from backend.app.geospatial.geotiff_handler import GeoTIFFHandler
from backend.app.config import DEMO_DATA_DIR

def test_geotiff_metadata_extraction():
    tif_path = DEMO_DATA_DIR / "himalaya_optical.tif"
    assert tif_path.exists(), "Demo GeoTIFF should exist"

    meta = GeoTIFFHandler.inspect_raster(str(tif_path))
    assert meta["is_georeferenced"] is True
    assert meta["crs"] is not None
    assert "32643" in meta["crs"]
    assert meta["width"] == 512
    assert meta["height"] == 512
    assert meta["bands_count"] == 3
    assert meta["gsd"] is not None
    assert meta["bounds"] is not None

def test_non_georeferenced_image_inspection():
    png_path = DEMO_DATA_DIR / "drone_coastal.png"
    assert png_path.exists()

    meta = GeoTIFFHandler.inspect_raster(str(png_path))
    assert meta["is_georeferenced"] is False
    assert meta["crs"] is None
    assert meta["width"] == 512
    assert meta["height"] == 512
