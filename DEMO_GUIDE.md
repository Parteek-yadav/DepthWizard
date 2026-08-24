# DepthWizard — 3-Minute SIH Jury Presentation Guide

## 🎯 Presentation Script & Flow

### Minute 0:00 - 0:45 | Problem Context & Dual-Pipeline Ingestion
- **Pitch**: *"Judges, single-view optical satellite images contain rich contextual elevation cues, but traditional monocular depth models only predict unitless depth and fail in metric geospatial applications. DepthWizard solves this by pairing monocular depth estimation with robust reference calibration."*
- **Action**: Open `http://127.0.0.1:8000/` $\rightarrow$ Show the clean header with **ISRO SIH26175** branding.
- **Action**: Click **Demo Datasets** $\rightarrow$ select **Himalayan Ridge & Valley (Georeferenced GeoTIFF)**.

---

### Minute 0:45 - 1:45 | Multi-Pane Comparative Pipeline & Calibration
- **Action**: Switch across the tabs:
  1. **Optical RGB**: Show raw satellite tile.
  2. **Relative Depth**: Show fine micro-relief features inferred by Depth Anything V2.
  3. **Digital Surface Model (DSM)**: Point to the calibrated metric heights ($850\text{m} - 2450\text{m}$).
  4. **4-Pane Split**: Show that all four representations are synchronized.
- **Highlight**: Point to the **Calibration Report Card** in the right sidebar:
  - Explain the **Huber M-estimation** that calibrated relative depth against SRTM reference data.
  - Highlight the measured **MAE, RMSE, and $R^2$ fit scores**.

---

### Minute 1:45 - 2:30 | 3D Flythrough & Structural Height Analysis
- **Action**: Switch back to **Interactive 3D Terrain**.
- **Action**: Click **Drone Fly** mode $\rightarrow$ Use `W/A/S/D` and mouse look to fly low across the mountain valleys.
- **Action**: Adjust the **Vertical Exaggeration** slider from $1.0\times$ to $2.5\times$ to demonstrate real-time vertex buffer scaling.
- **Action**: Move the **Sun Altitude** slider to showcase shadow casting across ridges.
- **Action**: In the right sidebar, use the **Structural Height & Slope Tool** to measure the elevation difference ($\Delta Z$) between the valley base and mountain summit.

---

### Minute 2:30 - 3:00 | Exports & Conclusion
- **Action**: Click **GeoTIFF Metric DSM** download $\rightarrow$ explain that original CRS (`EPSG:32643`) and affine transforms are preserved for GIS software (QGIS/ArcGIS).
- **Action**: Click **3D Wavefront Mesh (.OBJ)** download.
- **Closing**: *"DepthWizard bridges the gap between zero-shot computer vision and rigorous geospatial photogrammetry, providing an immediate, actionable elevation workflow for ISRO remote sensing missions."*
