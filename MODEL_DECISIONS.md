# DepthWizard -- Model Decisions & Evaluation

## 1. Monocular Depth Backbone Candidates Evaluated

| Model Candidate | Resolution | Latency (CPU) | Zero-Shot Quality | License | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Depth Anything V2 (Small)** | 518x518 | ~330ms (ONNX) | **State-of-the-Art (Dense Micro-Relief)** | Apache 2.0 | **Primary Selected** |
| **DPT (Dense Prediction Transformer)** | 384x384 | ~3.5s | Good general depth, softer edges | MIT | Candidate |
| **MiDaS v3.1 (DPT-Large)** | 384x384 | ~5.2s | High latency, heavy memory | MIT | Alternative |
| **Marigold (Diffusion-based)** | 768x768 | ~25s (GPU only) | Photorealistic, but unusable without high-end GPU | Apache 2.0 | Infeasible for Real-time |

---

## 2. Selection Rationale: Depth Anything V2

1. **Edge Sharpness**: Depth Anything V2 excels at preserving high-frequency edges around building rooftops, ridge crests, and cliff margins.
2. **Computational Efficiency**: The `vits` small variant is lightweight enough to run reliably on CPU without freezing hackathon laptops.
3. **ONNX & PyTorch Compatibility**: Supports native ONNX runtime with CPU and CUDA execution providers.
4. **Structural Fallback Adapter**: Integrated gradient-photogrammetric estimator to ensure zero-crash execution across any restricted testing environment.

---

## 3. Setup: Downloading Model Weights

The real ONNX model weights are **not bundled in the repository** (they are ~95 MB). After cloning, you must run:

```bash
python scripts/download_models.py
```

This downloads `depth_anything_v2_vits.onnx` from [onnx-community/depth-anything-v2-small](https://huggingface.co/onnx-community/depth-anything-v2-small) on Hugging Face into `backend/cache/`. The download is idempotent (skips if the file already exists).

**If this step is skipped**, the system automatically engages the **structural fallback estimator** -- a hand-crafted heuristic using Gaussian blur, luminance, and texture energy. This fallback is clearly labeled as such in:
- Backend API responses (`model_metadata.is_fallback = true`)
- Frontend header badge (amber "Structural Fallback" indicator)
- Server logs

The fallback is a legitimate zero-crash safety net, but it is **not** a learned depth model and should not be presented as one.

---

## 4. Remote Sensing Adaptation

Standard monocular depth models trained on natural outdoor scenes (KITTI, NYUv2) assume horizontal camera orientation. For nadir and oblique aerial remote-sensing:
- Multi-scale spectral decomposition is applied to separate low-frequency regional topography from high-frequency structural height.
- Luminance and local contrast normalization prevents cloud/water reflection artifacts from corrupting relative elevation.
- Scale and offset are grounded by empirical reference elevation datasets (SRTM / COP30 / GCPs).

---

## 5. Validation

See [MODEL_VALIDATION_RESULTS.md](MODEL_VALIDATION_RESULTS.md) for side-by-side calibration metrics comparing the real ONNX model against the structural fallback.
