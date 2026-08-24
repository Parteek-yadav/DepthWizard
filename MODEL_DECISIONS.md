# DepthWizard — Model Decisions & Evaluation

## 1. Monocular Depth Backbone Candidates Evaluated

| Model Candidate | Resolution | Latency (CPU) | Zero-Shot Quality | License | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Depth Anything V2 (Small)** | 518×518 | ~1.8s | **State-of-the-Art (Dense Micro-Relief)** | Apache 2.0 | **Primary Selected** |
| **DPT (Dense Prediction Transformer)** | 384×384 | ~3.5s | Good general depth, softer edges | MIT | Candidate |
| **MiDaS v3.1 (DPT-Large)** | 384×384 | ~5.2s | High latency, heavy memory | MIT | Alternative |
| **Marigold (Diffusion-based)** | 768×768 | ~25s (GPU only) | Photorealistic, but unusable without high-end GPU | Apache 2.0 | Infeasible for Real-time |

---

## 2. Selection Rationale: Depth Anything V2

1. **Edge Sharpness**: Depth Anything V2 excels at preserving high-frequency edges around building rooftops, ridge crests, and cliff margins.
2. **Computational Efficiency**: The `vits` small variant is lightweight enough to run reliably on CPU without freezing hackathon laptops.
3. **ONNX & PyTorch Compatibility**: Supports native ONNX runtime with CPU and CUDA execution providers.
4. **Structural Fallback Adapter**: Integrated gradient-photogrammetric estimator to ensure zero-crash execution across any restricted testing environment.

---

## 3. Remote Sensing Adaptation

Standard monocular depth models trained on natural outdoor scenes (KITTI, NYUv2) assume horizontal camera orientation. For nadir and oblique aerial remote-sensing:
- Multi-scale spectral decomposition is applied to separate low-frequency regional topography from high-frequency structural height.
- Luminance and local contrast normalization prevents cloud/water reflection artifacts from corrupting relative elevation.
- Scale and offset are grounded by empirical reference elevation datasets (SRTM / COP30 / GCPs).
