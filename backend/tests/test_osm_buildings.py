# backend/tests/test_osm_buildings.py
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.geospatial.osm_buildings import OSMBuildingFetcher
from backend.app.geospatial.geo_fetcher import GeoFetcher

client = TestClient(app)

def test_osm_overpass_json_parsing():
    """Verify that Overpass JSON elements are correctly parsed into real polygon footprints."""
    mock_overpass_data = {
        "elements": [
            {"type": "node", "id": 1, "lat": 26.9230, "lon": 75.8260},
            {"type": "node", "id": 2, "lat": 26.9235, "lon": 75.8260},
            {"type": "node", "id": 3, "lat": 26.9235, "lon": 75.8268},
            {"type": "node", "id": 4, "lat": 26.9230, "lon": 75.8268},
            {
                "type": "way",
                "id": 101,
                "nodes": [1, 2, 3, 4, 1],
                "tags": {
                    "building": "commercial",
                    "name": "Jaipur Tech Complex",
                    "building:levels": "5",
                    "height": "17.0"
                }
            }
        ]
    }

    buildings = OSMBuildingFetcher.parse_overpass_response(
        mock_overpass_data,
        center_lat=26.9232,
        center_lon=26.8264
    )

    assert len(buildings) == 1
    bldg = buildings[0]
    assert bldg["is_real_osm"] is True
    assert bldg["name"] == "Jaipur Tech Complex"
    assert bldg["height_meters"] == 17.0
    assert len(bldg["polygon_meters"]) == 4
    assert bldg["material"]["category"] == "commercial"
    assert bldg["material"]["facade_color"] == "#386b8c"

def test_mountain_region_has_zero_fake_buildings():
    """Verify that uninhabited / mountainous terrain returns 0 fake buildings."""
    # Mount Everest coordinates
    min_lat, min_lon, max_lat, max_lon = 27.980, 86.920, 27.995, 86.935
    bldgs = OSMBuildingFetcher.get_known_landmark_footprints(center_lat=27.9881, center_lon=86.9250)
    assert len(bldgs) == 0

def test_api_returns_real_polygon_footprints():
    """Verify POST /api/geo/process_selected_rect returns real polygon vertices."""
    res = client.post("/api/geo/process_selected_rect", json={
        "min_lon": 75.820,
        "min_lat": 26.918,
        "max_lon": 75.832,
        "max_lat": 26.928,
        "name": "Jaipur City Palace & Hawa Mahal",
        "mesh_resolution": 64,
        "height_exaggeration": 1.0
    })

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "buildings" in data
    assert len(data["buildings"]) > 0

    first_bldg = data["buildings"][0]
    assert "polygon_meters" in first_bldg
    assert len(first_bldg["polygon_meters"]) >= 3
    assert "centroid_meters" in first_bldg
    assert "base_elevation_meters" in first_bldg
    assert first_bldg["is_real_osm"] is True
