# backend/tests/test_ai_supervisor.py
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.ml.ai_supervisor import ReconstructionSupervisor

client = TestClient(app)

def test_depth_quality_assessment():
    """Verify mathematical depth assessment metrics."""
    # Good diverse synthetic depth array
    H, W = 64, 64
    x = np.linspace(0, 1, W)
    y = np.linspace(0, 1, H)
    X, Y = np.meshgrid(x, y)
    good_depth = (X + Y).astype(np.float32)

    res = ReconstructionSupervisor.assess_depth_quality(good_depth)
    assert res["is_suitable_for_mesh"] is True
    assert res["quality_score"] > 0.6
    assert res["invalid_pixel_percentage"] == 0.0
    assert res["edge_energy"] > 0.0

def test_flat_depth_quality_penalty():
    """Verify that completely flat depth maps trigger quality warnings."""
    flat_depth = np.full((64, 64), 0.5, dtype=np.float32)
    res = ReconstructionSupervisor.assess_depth_quality(flat_depth)
    assert any("flat" in w.lower() for w in res["warnings"])
    assert res["quality_score"] < 0.8

def test_reconstruction_supervisor_deterministic_fallback():
    """Verify structured decision output from supervisor with deterministic fallback."""
    decision = ReconstructionSupervisor.analyze_reconstruction_context(
        scene_type="Georeferenced Test Area",
        geographic_bounds={"min_lon": 75.8, "min_lat": 26.9, "max_lon": 75.81, "max_lat": 26.91},
        dimensions_meters={"width": 1100.0, "height": 1100.0},
        terrain_stats={"min_meters": 420.0, "max_meters": 490.0},
        building_count=12,
        has_dem=True
    )

    assert "scene_type" in decision
    assert "terrain_complexity" in decision
    assert "recommended_terrain_lod" in decision
    assert "recommended_mesh_resolution" in decision
    assert decision["recommended_mesh_resolution"] in [64, 128, 256]
    assert "data_confidence" in decision
    assert decision["data_confidence"] in ["HIGH", "MEDIUM", "LOW"]
    assert "recommended_actions" in decision
    assert len(decision["recommended_actions"]) > 0

def test_api_returns_supervisor_decision_and_provenance():
    """Verify POST /api/geo/process_selected_rect includes supervisor decision & provenance."""
    res = client.post("/api/geo/process_selected_rect", json={
        "min_lon": 75.820,
        "min_lat": 26.918,
        "max_lon": 75.832,
        "max_lat": 26.928,
        "name": "Jaipur AI Supervised Area",
        "mesh_resolution": 64,
        "height_exaggeration": 1.0
    })

    assert res.status_code == 200
    data = res.json()
    assert "supervisor_decision" in data
    assert "data_provenance" in data
    assert "terrain_source" in data["data_provenance"]
    assert "imagery_source" in data["data_provenance"]
    assert "building_source" in data["data_provenance"]
    assert data["supervisor_decision"]["data_confidence"] == "HIGH"
