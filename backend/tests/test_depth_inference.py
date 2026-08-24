# backend/tests/test_depth_inference.py
import pytest
import numpy as np
from backend.app.ml.model_manager import ModelManager
from backend.app.ml.colormap_utils import apply_scientific_colormap

def test_depth_model_predict():
    manager = ModelManager.get_instance()
    model = manager.get_depth_model()
    assert model is not None

    # Dummy RGB image (128x128x3)
    rgb = (np.random.rand(128, 128, 3) * 255).astype(np.uint8)
    depth = model.predict(rgb)

    assert depth.shape == (128, 128)
    assert depth.dtype == np.float32
    assert 0.0 <= np.min(depth) <= 1.0
    assert 0.0 <= np.max(depth) <= 1.0

def test_colormap_utility():
    dummy_depth = np.linspace(0, 1, 100).reshape(10, 10).astype(np.float32)
    colored = apply_scientific_colormap(dummy_depth, colormap_name="turbo")
    assert colored.shape == (10, 10, 3)
    assert colored.dtype == np.uint8
