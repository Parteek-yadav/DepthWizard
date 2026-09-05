# backend/tests/test_demo_mode.py
import os
import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import OUTPUTS_DIR
import backend.app.config as config
from backend.app.geospatial.geo_fetcher import GeoFetcher
from backend.app.geospatial.osm_buildings import OSMBuildingFetcher
from backend.app.ml.ai_supervisor import ReconstructionSupervisor
from backend.app.api.routes_demo import CURATED_DEMO_LOCATIONS, prewarm_demo_cache

client = TestClient(app)


def test_health_reports_demo_mode():
    """Verify that /api/health endpoint includes demo_mode field."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "demo_mode" in data
    assert isinstance(data["demo_mode"], bool)


def test_search_locations_skips_nominatim_when_demo_mode(monkeypatch):
    """Verify Nominatim live fetch is bypassed when DEMO_MODE=True."""
    monkeypatch.setattr("backend.app.geospatial.geo_fetcher.DEMO_MODE", True)

    def fail_on_call(*args, **kwargs):
        raise AssertionError("Live Nominatim search was called during DEMO_MODE!")

    monkeypatch.setattr(GeoFetcher, "_fetch_nominatim_search", fail_on_call)

    # Search known gazetteer entry
    results = GeoFetcher.search_locations("Jaipur")
    assert len(results) > 0
    assert any("Jaipur" in r["name"] for r in results)


def test_osm_buildings_skips_overpass_when_demo_mode(monkeypatch):
    """Verify Overpass API is bypassed when DEMO_MODE=True."""
    monkeypatch.setattr("backend.app.geospatial.osm_buildings.DEMO_MODE", True)

    def fail_on_urlopen(*args, **kwargs):
        raise AssertionError("Live Overpass network request was called during DEMO_MODE!")

    monkeypatch.setattr("urllib.request.urlopen", fail_on_urlopen)

    bldgs = OSMBuildingFetcher.fetch_real_building_footprints(
        min_lon=75.820, min_lat=26.918, max_lon=75.832, max_lat=26.928,
        center_lat=26.9239, center_lon=75.8267
    )
    assert len(bldgs) > 0
    assert any("Hawa Mahal" in b.get("name", "") for b in bldgs)


def test_ai_supervisor_skips_openrouter_when_demo_mode(monkeypatch):
    """Verify OpenRouter network request is bypassed when DEMO_MODE=True."""
    monkeypatch.setattr("backend.app.ml.ai_supervisor.DEMO_MODE", True)

    def fail_on_urlopen(*args, **kwargs):
        raise AssertionError("OpenRouter network request was made during DEMO_MODE!")

    monkeypatch.setattr("urllib.request.urlopen", fail_on_urlopen)

    decision = ReconstructionSupervisor.analyze_reconstruction_context(
        scene_type="Test Scene",
        geographic_bounds={"min_lon": 75.8, "min_lat": 26.9, "max_lon": 75.9, "max_lat": 27.0},
        dimensions_meters={"width": 1000.0, "height": 1000.0},
        terrain_stats={"min_meters": 100.0, "max_meters": 250.0},
        building_count=5,
        has_dem=True
    )
    assert decision["supervisor_mode"] == "DETERMINISTIC_RULE_BASED"
    assert "data_confidence" in decision


def test_scripted_run_prewarms_disk_cache(monkeypatch):
    """Verify /api/demo/scripted_run pre-warms and saves disk artifacts under reserved task_ids."""
    monkeypatch.setattr("backend.app.geospatial.osm_buildings.DEMO_MODE", True)
    monkeypatch.setattr("backend.app.geospatial.geo_fetcher.DEMO_MODE", True)
    monkeypatch.setattr("backend.app.ml.ai_supervisor.DEMO_MODE", True)

    res = client.get("/api/demo/scripted_run")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert len(data["prewarmed_locations"]) == len(CURATED_DEMO_LOCATIONS)

    for loc_id in data["prewarmed_locations"]:
        task_dir = OUTPUTS_DIR / loc_id
        assert task_dir.exists()
        assert (task_dir / "report.json").exists()
        assert (task_dir / "mesh.json").exists()
        assert (task_dir / "texture.png").exists()


def test_curated_locations_building_centroids_within_mesh_bounds(monkeypatch):
    """
    CRITICAL INTEGRATION TEST:
    Assert that for EVERY curated demo location, every building's centroid_meters
    (x, z) falls strictly inside the terrain mesh.bounds_meters range [min_x, min_z, max_x, max_z].
    This guarantees OSM buildings never render floating in void outside the terrain.
    """
    monkeypatch.setattr("backend.app.geospatial.osm_buildings.DEMO_MODE", True)
    monkeypatch.setattr("backend.app.geospatial.geo_fetcher.DEMO_MODE", True)
    monkeypatch.setattr("backend.app.ml.ai_supervisor.DEMO_MODE", True)

    # Pre-warm or execute each curated location
    prewarm_demo_cache()

    for loc in CURATED_DEMO_LOCATIONS:
        payload = {
            "min_lon": loc["min_lon"],
            "min_lat": loc["min_lat"],
            "max_lon": loc["max_lon"],
            "max_lat": loc["max_lat"],
            "name": loc["name"],
            "mesh_resolution": loc["mesh_resolution"],
            "height_exaggeration": loc["height_exaggeration"]
        }
        res = client.post("/api/geo/process_selected_rect", json=payload)
        assert res.status_code == 200
        result = res.json()

        mesh = result["mesh"]
        bounds = mesh["bounds_meters"]
        if isinstance(bounds, dict):
            min_x, max_x = bounds["min_x"], bounds["max_x"]
            min_z, max_z = bounds["min_z"], bounds["max_z"]
        else:
            min_x, max_x = bounds[0], bounds[1]
            min_z, max_z = bounds[4], bounds[5]
        buildings = result.get("buildings", [])

        assert len(buildings) > 0, f"Expected buildings for curated landmark {loc['name']}, found none!"

        for bldg in buildings:
            cx = bldg["centroid_meters"]["x"]
            cz = bldg["centroid_meters"]["z"]
            
            # Assert building centroid is inside mesh bounds
            assert min_x <= cx <= max_x, (
                f"Building {bldg.get('name', bldg.get('id'))} in {loc['name']} has centroid x={cx} "
                f"outside mesh bounds [{min_x}, {max_x}]"
            )
            assert min_z <= cz <= max_z, (
                f"Building {bldg.get('name', bldg.get('id'))} in {loc['name']} has centroid z={cz} "
                f"outside mesh bounds [{min_z}, {max_z}]"
            )

            # Also assert all polygon vertices are within bounds
            for pt in bldg.get("polygon_meters", []):
                px, pz = pt[0], pt[1]
                assert min_x <= px <= max_x, (
                    f"Polygon vertex {pt} in building {bldg.get('name')} exceeds x bounds [{min_x}, {max_x}]"
                )
                assert min_z <= pz <= max_z, (
                    f"Polygon vertex {pt} in building {bldg.get('name')} exceeds z bounds [{min_z}, {max_z}]"
                )


def test_routes_geo_serves_disk_cache(monkeypatch):
    """Verify that process_selected_rect returns the pre-warmed disk cache immediately."""
    jaipur_loc = CURATED_DEMO_LOCATIONS[0]
    payload = {
        "min_lon": jaipur_loc["min_lon"],
        "min_lat": jaipur_loc["min_lat"],
        "max_lon": jaipur_loc["max_lon"],
        "max_lat": jaipur_loc["max_lat"],
        "name": jaipur_loc["name"]
    }

    # Ensure disk cache exists
    prewarm_demo_cache()
    disk_report = OUTPUTS_DIR / jaipur_loc["id"] / "report.json"
    assert disk_report.exists()

    # The route should load directly from report.json without recomputing
    res = client.post("/api/geo/process_selected_rect", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["geographic_context"]["name"] == jaipur_loc["name"]
    assert len(data["buildings"]) > 0
