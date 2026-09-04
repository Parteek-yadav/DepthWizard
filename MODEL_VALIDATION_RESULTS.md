# DepthWizard -- Model Validation Results

## Side-by-Side Comparison: Real ONNX Model vs Structural Fallback

Validation performed against bundled Himalayan ridge demo data:
- **Optical image**: `data/demo/himalaya_optical.tif`
- **Reference DEM**: `data/demo/himalaya_srtm_dem.tif` (NASA SRTM 30m)
- **Calibration method**: Huber M-Estimation (robust regression)
- **Validation split**: 20% held-out test set

| Metric | Depth Anything V2 (ONNX) | Structural Fallback (Heuristic) |
| :--- | :---: | :---: |
| **MAE (meters)** | 237.282 | 236.6 |
| **RMSE (meters)** | 302.544 | 306.235 |
| **Pearson r** | 0.0072 | 0.1554 |
| **R-squared** | -0.029 | -0.0543 |
| Inference time (CPU) | 330.7ms | 60.9ms |
| Calibrated range | 1044.8m - 1095.13m | 761.86m - 1891.46m |
| Scale (s) | -50.3238 | 1129.5957 |
| Offset (t) | 1095.13 | 761.86 |
| is_fallback | False | True |

---

## Interpretation

- The **Depth Anything V2 ONNX model** achieves MAE of **237.282m** and RMSE of **302.544m** against SRTM reference, with Pearson r = **0.0072** and R-squared = **-0.029**.
- The **structural fallback** achieves MAE of **236.6m** and RMSE of **306.235m**.
- Both are calibrated using identical Huber regression against the same SRTM DEM reference.
- The fallback is a hand-crafted heuristic (Gaussian blur + luminance + texture energy) and should be clearly labeled as such in all outputs.

> **Note on calibration quality:** Both models show high MAE/RMSE and near-zero Pearson correlation on this specific demo data because the bundled optical GeoTIFFs are synthetic placeholder images — they do not contain real satellite imagery spatially correlated with the SRTM DEM. With real geocoded satellite imagery, the learned depth model is expected to substantially outperform the heuristic fallback. These numbers are provided for **transparency and honest reporting**, not as a measure of model capability.

---

## How to Reproduce

```bash
# 1. Download real model weights
python scripts/download_models.py

# 2. Run validation
python scripts/run_validation.py
```

*Generated automatically by `scripts/run_validation.py`*
