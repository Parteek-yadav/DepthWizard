# backend/tests/test_depth_inference.py
import pytest
import numpy as np
from pathlib import Path
from backend.app.ml.depth_anything_v2 import DepthAnythingV2Model
from backend.app.ml.colormap_utils import apply_scientific_colormap

# Path to the ONNX weights file
ONNX_WEIGHTS_PATH = Path(__file__).parent.parent / "cache" / "depth_anything_v2_vits.onnx"


class TestDepthModelFallbackPath:
    """Tests for the structural fallback path (when ONNX weights are absent)."""

    def test_depth_model_fallback_predict(self):
        """Verify fallback path produces valid depth maps when ONNX weights are absent."""
        model = DepthAnythingV2Model(model_name="nonexistent_model_for_fallback_test")
        model.load(device="cpu")

        # Must engage fallback since the model file doesn't exist
        assert model.is_fallback is True
        assert model.session is None

        # Dummy RGB image (128x128x3)
        rgb = (np.random.rand(128, 128, 3) * 255).astype(np.uint8)
        depth = model.predict(rgb)

        assert depth.shape == (128, 128)
        assert depth.dtype == np.float32
        assert 0.0 <= np.min(depth) <= 1.0
        assert 0.0 <= np.max(depth) <= 1.0

    def test_fallback_metadata_reports_fallback(self):
        """Verify fallback model metadata correctly reports is_fallback=True."""
        model = DepthAnythingV2Model(model_name="nonexistent_model_for_fallback_test")
        model.load(device="cpu")

        meta = model.get_metadata()
        assert meta["is_fallback"] is True
        assert "Fallback" in meta["backbone"]


@pytest.mark.skipif(
    not ONNX_WEIGHTS_PATH.exists(),
    reason=f"ONNX weights not found at {ONNX_WEIGHTS_PATH}. Run 'python scripts/download_models.py' first."
)
class TestDepthModelONNXPath:
    """Tests for the real ONNX model path (requires downloaded weights)."""

    def test_onnx_model_loads_successfully(self):
        """Verify real ONNX model loads and is_fallback is False."""
        model = DepthAnythingV2Model(model_name="depth_anything_v2_vits")
        result = model.load(device="cpu")

        assert result is True
        assert model.is_fallback is False
        assert model.session is not None

    def test_onnx_inference_output(self):
        """Verify real ONNX model produces correct output shape/range on random input."""
        model = DepthAnythingV2Model(model_name="depth_anything_v2_vits")
        model.load(device="cpu")

        # Test with 256x256 random RGB image
        rgb = (np.random.rand(256, 256, 3) * 255).astype(np.uint8)
        depth = model.predict(rgb)

        assert depth.shape == (256, 256), f"Expected (256, 256), got {depth.shape}"
        assert depth.dtype == np.float32
        assert 0.0 <= np.min(depth) <= 1.0
        assert 0.0 <= np.max(depth) <= 1.0
        # Real model should produce non-trivial depth variation
        assert np.std(depth) > 0.01, "ONNX model produced near-constant output"

    def test_onnx_metadata_reports_real_model(self):
        """Verify real ONNX model metadata correctly reports is_fallback=False."""
        model = DepthAnythingV2Model(model_name="depth_anything_v2_vits")
        model.load(device="cpu")

        meta = model.get_metadata()
        assert meta["is_fallback"] is False
        assert "ONNX" in meta["backbone"]
        assert meta["model_name"] == "depth_anything_v2_vits"

    def test_onnx_non_square_input(self):
        """Verify ONNX model handles non-square input images correctly."""
        model = DepthAnythingV2Model(model_name="depth_anything_v2_vits")
        model.load(device="cpu")

        # Non-square: 480x640
        rgb = (np.random.rand(480, 640, 3) * 255).astype(np.uint8)
        depth = model.predict(rgb)

        assert depth.shape == (480, 640), f"Expected (480, 640), got {depth.shape}"
        assert depth.dtype == np.float32


def test_colormap_utility():
    dummy_depth = np.linspace(0, 1, 100).reshape(10, 10).astype(np.float32)
    colored = apply_scientific_colormap(dummy_depth, colormap_name="turbo")
    assert colored.shape == (10, 10, 3)
    assert colored.dtype == np.uint8
