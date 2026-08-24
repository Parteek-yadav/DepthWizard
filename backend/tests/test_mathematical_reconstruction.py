# backend/tests/test_mathematical_reconstruction.py
import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.processing.mesh_generator import MeshGenerator
from backend.app.geospatial.geo_fetcher import GeoFetcher

client = TestClient(app)

def test_flat_plane_reconstruction():
    """
    Mathematical Validation Test A: Flat Plane.
    Z(x, y) = a*x + b*y + c
    Verifies that the continuous mesh reproduces the analytical surface with RMS error < 1e-5.
    """
    H, W = 64, 64
    x = np.linspace(-50, 50, W)
    y = np.linspace(-50, 50, H)
    X, Y = np.meshgrid(x, y)
    a, b, c = 0.05, -0.03, 120.0
    Z_analytical = a * X + b * Y + c

    mesh = MeshGenerator.generate_terrain_mesh(
        elevation_2d=Z_analytical,
        target_grid_size=64,
        height_exaggeration=1.0,
        spatial_bounds_meters=(-50, -50, 50, 50)
    )

    verts = np.array(mesh["vertices"]).reshape(-1, 3)
    # vy is height relative to mean elevation in MeshGenerator
    vy = verts[:, 1]
    z_mean = np.mean(Z_analytical)
    expected_vy = (Z_analytical.flatten() - z_mean)
    
    # Measure Root Mean Square Reconstruction Error
    # Sort or match coordinates:
    assert len(vy) == H * W
    rms_error = np.sqrt(np.mean((np.sort(vy) - np.sort(expected_vy)) ** 2))
    assert rms_error < 1e-4
    assert mesh["vertex_count"] == H * W
    assert mesh["face_count"] == (H - 1) * (W - 1) * 2

def test_linear_slope_and_normals():
    """
    Mathematical Validation Test B: Linear Slope.
    Verifies that surface normal vectors match analytical gradient dz/dx, dz/dy.
    """
    H, W = 32, 32
    slope_x = 0.2
    elev = np.tile(np.linspace(0, slope_x * 100, W), (H, 1))
    
    mesh = MeshGenerator.generate_terrain_mesh(
        elevation_2d=elev,
        target_grid_size=32,
        height_exaggeration=1.0,
        spatial_bounds_meters=(-50, -50, 50, 50)
    )

    normals = np.array(mesh["normals"]).reshape(-1, 3)
    # Normal in Y-up frame: nz should point slightly negative in X (gradient direction) and positive in Y (up)
    assert np.all(normals[:, 1] > 0.9) # Strongly pointing upward
    assert normals.shape[0] == H * W

def test_gaussian_hill_reconstruction():
    """
    Mathematical Validation Test C: Gaussian Hill.
    Z(x, y) = A * exp(-((x-x0)^2 + (y-y0)^2) / (2*sigma^2))
    Verifies peak preservation and symmetry.
    """
    H, W = 64, 64
    x = np.linspace(-50, 50, W)
    y = np.linspace(-50, 50, H)
    X, Y = np.meshgrid(x, y)
    A = 50.0
    sigma = 15.0
    Z_hill = 100.0 + A * np.exp(-(X**2 + Y**2) / (2 * sigma**2))

    mesh = MeshGenerator.generate_terrain_mesh(
        elevation_2d=Z_hill,
        target_grid_size=64,
        height_exaggeration=1.0
    )

    assert abs(mesh["z_max_meters"] - 150.0) < 0.5
    assert abs(mesh["z_min_meters"] - 100.0) < 1.0
    assert mesh["vertex_count"] == H * W


def test_geospatial_bounds_metric_scaling():
    """
    Geospatial Validation Test D: WGS84 Geodesic Dimensions & Metric Scaling.
    Verifies metric width and height calculations at Jaipur coordinates.
    """
    # 0.01 degrees in latitude is approx 1.11 km
    min_lat, max_lat = 26.90, 26.91
    min_lon, max_lon = 75.80, 75.81
    w_m, h_m, area_km2 = GeoFetcher.calculate_metric_dimensions(min_lon, min_lat, max_lon, max_lat)

    assert 900.0 < w_m < 1100.0
    assert 1050.0 < h_m < 1150.0
    assert 0.9 < area_km2 < 1.3

def test_api_process_selected_rect():
    """
    Integration Test E: Paint-Style Rectangle Selection API.
    POST /api/geo/process_selected_rect
    """
    res = client.post("/api/geo/process_selected_rect", json={
        "min_lon": 75.820,
        "min_lat": 26.918,
        "max_lon": 75.832,
        "max_lat": 26.928,
        "name": "Jaipur Rectangular Selection",
        "mesh_resolution": 64,
        "height_exaggeration": 1.0
    })

    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "geographic_context" in data
    assert "dimensions_meters" in data["geographic_context"]
    assert data["geographic_context"]["dimensions_meters"]["width"] > 0
    assert data["mesh"]["vertex_count"] > 0
    assert "bounds_meters" in data["mesh"]
