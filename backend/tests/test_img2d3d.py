# backend/tests/test_img2d3d.py
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import TEMP_DIR
from backend.app.geospatial.geo_fetcher import GeoFetcher

client = TestClient(app)

def test_coordinate_parsing_and_validation():
    """Verify coordinate parser correctly parses and validates diverse formats."""
    # 1. Comma separated
    res1 = GeoFetcher.parse_coordinates("26.9124, 75.7873")
    assert res1 is not None
    assert abs(res1["lat"] - 26.9124) < 1e-4
    assert abs(res1["lon"] - 75.7873) < 1e-4

    # 2. Space separated
    res2 = GeoFetcher.parse_coordinates("28.6129 77.2295")
    assert res2 is not None
    assert abs(res2["lat"] - 28.6129) < 1e-4

    # 3. Invalid out-of-range coordinates
    res_inv1 = GeoFetcher.parse_coordinates("95.0, 75.0")
    assert res_inv1 is None

    res_inv2 = GeoFetcher.parse_coordinates("26.0, 210.0")
    assert res_inv2 is None


def test_convert_2d_photo_to_3d():
    """Verify dedicated 2D image to 3D reconstruction pipeline."""
    # Create test synthetic RGB photograph
    test_photo_path = TEMP_DIR / "test_photo_input.png"
    arr = np.random.randint(50, 200, (128, 128, 3), dtype=np.uint8)
    Image.fromarray(arr).save(str(test_photo_path))

    with open(test_photo_path, "rb") as f:
        response = client.post(
            "/api/img2d3d/convert",
            files={"file": ("test_photo.png", f, "image/png")},
            data={"depth_strength": "1.8", "mesh_resolution": "64"}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "Monocular depth-derived 3D" in data["type"]
    assert data["mesh"]["vertex_count"] > 0
    assert "urls" in data
    assert "texture" in data["urls"]
    assert "depth_map" in data["urls"]
    assert "obj_mesh" in data["urls"]
