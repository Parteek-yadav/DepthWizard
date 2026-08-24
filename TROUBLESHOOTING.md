# DepthWizard — Troubleshooting & Diagnostics Guide

## 1. Common Issues & Solutions

### A. WebGL 3D Viewport Not Rendering
- **Symptom**: Black screen in the 3D viewport.
- **Fix**: Verify Hardware Acceleration is enabled in your browser settings (`chrome://settings/system` or `edge://settings/system`).
- **Fix**: Click **Fit & Reset Camera** in the left floating controls to re-center the perspective frustum.

### B. GeoTIFF Missing CRS Warning
- **Symptom**: `Dataset has no geotransform, gcps, or rpcs` in logs.
- **Explanation**: This occurs when uploading non-georeferenced images (PNG/JPG) or unreferenced TIFFs.
- **Resolution**: The system automatically and gracefully transitions to **Mode 1: Non-Georeferenced (Relative rDSM)** and explicitly marks heights as relative units.

### C. Port 8000 Already in Use
- **Symptom**: `[Errno 10048] error while attempting to bind on address ('127.0.0.1', 8000)`.
- **Fix**: Launch on an alternative port:
  ```bash
  python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8080 --reload
  ```

---

## 2. Performance Tuning

- **Mesh Resolution**: Defaults to a $128 \times 128$ vertex grid ($16,384$ vertices), providing a silky-smooth 60 FPS WebGL rendering experience on standard integrated GPUs.
- **Large Rasters**: Optical satellite tiles larger than $2048 \times 2048$ are automatically downsampled using anti-aliased bilinear interpolation before mesh generation to prevent WebGL buffer overflow.
- **Hardware Acceleration**: Automatically detects NVIDIA CUDA GPUs via PyTorch / ONNX Runtime; seamlessly falls back to optimized multi-threaded CPU execution when GPUs are unavailable.
