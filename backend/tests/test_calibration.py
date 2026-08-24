# backend/tests/test_calibration.py
import pytest
import numpy as np
from backend.app.geospatial.calibrator import ElevationCalibrator
from backend.app.geospatial.gcp_manager import GCPManager, GroundControlPoint

def test_dem_huber_calibration():
    # Synthetic relative depth field
    np.random.seed(42)
    rel_depth = np.random.uniform(0.1, 0.9, (100, 100)).astype(np.float32)
    # Synthetic true elevation (scale=1500, offset=800 + noise)
    true_scale = 1500.0
    true_offset = 800.0
    ref_dem = true_scale * rel_depth + true_offset + np.random.normal(0, 10.0, (100, 100)).astype(np.float32)

    calibrated_dsm, metrics = ElevationCalibrator.calibrate_from_dem(rel_depth, ref_dem)

    assert calibrated_dsm.shape == (100, 100)
    assert abs(metrics["scale"] - true_scale) < 50.0
    assert abs(metrics["offset"] - true_offset) < 50.0
    assert metrics["rmse_meters"] < 25.0
    assert metrics["r2_score"] > 0.85
    assert metrics["pearson_r"] > 0.90

def test_gcp_calibration():
    rel_depth = np.linspace(0.1, 0.9, 10000).reshape(100, 100).astype(np.float32)
    gcps = [
        GroundControlPoint(id="1", pixel_x=10.0, pixel_y=10.0, elevation_meters=200.0),
        GroundControlPoint(id="2", pixel_x=50.0, pixel_y=50.0, elevation_meters=600.0),
        GroundControlPoint(id="3", pixel_x=90.0, pixel_y=90.0, elevation_meters=1000.0)
    ]
    d_samples, z_samples = GCPManager.sample_gcp_pairs(gcps, rel_depth)
    assert len(d_samples) == 3

    calibrated_dsm, metrics = ElevationCalibrator.calibrate_from_gcps(rel_depth, d_samples, z_samples)
    assert calibrated_dsm.shape == (100, 100)
    assert metrics["gcp_count"] == 3
