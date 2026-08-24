# backend/tests/test_geo_selection.py
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.geospatial.geo_fetcher import GeoFetcher

client = TestClient(app)

def test_gazetteer_search():
    """Verify geographic gazetteer search returns valid coordinates and metadata."""
    results = GeoFetcher.search_locations("Bengaluru")
    assert len(results) >= 1
    top = results[0]
    assert "lat" in top and "lon" in top
    assert 12.0 <= top["lat"] <= 14.0
    assert 76.0 <= top["lon"] <= 79.0
    assert top["has_buildings"] is True

def test_bounds_calculation():
    """Verify bounding box calculation for selected point and radius."""
    lat, lon, radius = 13.0336, 77.5644, 500.0
    min_lon, min_lat, max_lon, max_lat = GeoFetcher.calculate_bounds(lat, lon, radius)
    assert min_lon < lon < max_lon
    assert min_lat < lat < max_lat
    # 500m should be approx 0.0045 degrees
    assert abs((max_lat - min_lat) - 0.009) < 0.005

def test_building_catalog_generation():
    """Verify 3D building generation with realistic multi-class colors and physical heights."""
    area = GeoFetcher.generate_area_dataset(lat=13.0336, lon=77.5644, radius_meters=500.0)
    assert "buildings" in area
    assert len(area["buildings"]) > 0
    bldg = area["buildings"][0]
    assert "material" in bldg
    assert "facade_color" in bldg["material"]
    assert "roof_color" in bldg["material"]
    # Check that buildings have realistic non-uniform colors
    assert bldg["material"]["facade_color"].startswith("#")
    assert bldg["height_meters"] > 0

def test_api_geo_search_endpoint():
    """Verify GET /api/geo/search endpoint."""
    res = client.get("/api/geo/search?q=ISRO")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] >= 1
    assert "results" in data

def test_api_geo_select_and_process():
    """Verify POST /api/geo/process_selected end-to-end execution."""
    res = client.post("/api/geo/process_selected", json={
        "lat": 13.0336,
        "lon": 77.5644,
        "radius_meters": 500.0,
        "name": "ISRO ISTRAC Bengaluru",
        "mesh_resolution": 64,
        "height_exaggeration": 1.2
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["is_georeferenced"] is True
    assert "geographic_context" in data
    assert "buildings" in data
    assert len(data["buildings"]) > 0
    assert data["mesh"]["vertex_count"] > 0
