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

---

## 🛡️ Controlled Demo Mode (`DEMO_MODE=true`)

For zero-latency, high-reliability jury presentations without internet dependence, DepthWizard includes a dedicated **Demo Mode**.

### Enabling Demo Mode
Add the following line to your `.env` file (or set in your environment):
```bash
DEMO_MODE=true
```

### What Happens in Demo Mode
1. **Network Independence**:
   - **POI Search**: Queries the offline `EXPANDED_GAZETTEER` (skips live Nominatim).
   - **3D Buildings**: Loads authentic curated landmark building polygons (skips live Overpass API calls, eliminating 3.5s timeout risks).
   - **AI Supervisor**: Runs in deterministic rule-based mode with guaranteed consistency (skips OpenRouter free tier API calls).
2. **Pre-warmed Disk Cache**:
   - On backend startup, the server pre-warms and caches full mesh, texture, and DSM assets under `data/outputs/demo_*` for instant sub-millisecond initial clicks.
3. **Transparent UI Indicator**:
   - The top navigation bar displays a distinct amber `[● DEMO MODE]` badge so judges and evaluators are clearly informed that a controlled offline dataset is being showcased.

### Guaranteed Reliable Presentation Locations
The following 4 curated locations have authentic vector building footprints and pre-warmed terrain:
| Landmark | Coordinates | Curated Buildings Included |
| :--- | :---: | :--- |
| **Jaipur City Palace & Hawa Mahal** | `26.9239°N, 75.8267°E` | Hawa Mahal, Mubarak Mahal, Chandra Mahal (7-storey) |
| **Taj Mahal & Yamuna Riverfront** | `27.1751°N, 78.0421°E` | Main Mausoleum (73m), West Mosque, East Jawab, Great Gate |
| **India Gate & Central Vista** | `28.6129°N, 77.2295°E` | 42m Memorial Arch, Canopy / Amar Jawan Jyoti, War Memorial |
| **ISRO ISTRAC Bengaluru** | `13.0336°N, 77.5644°E` | Mission Operations Complex (MOX-1), Deep Space Station, Telemetry Wing |

### Honesty in Reporting Philosophy (Note for Evaluators)
> **Pitch transparency**: When demonstrating in Demo Mode, inform the ISRO judges plainly:
> *"Judges, to ensure an uninterrupted, instant live demo independent of venue WiFi or public OSM API rate limits, DepthWizard is currently running in controlled Demo Mode. The terrain surfaces and building footprints shown here are authentic georeferenced data pre-cached locally for these landmarks, demonstrating the exact mathematical pipeline that runs in production."*
