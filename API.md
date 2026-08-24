# DepthWizard — REST API Documentation

## Base URL
```
http://127.0.0.1:8000
```

---

## Endpoints

### 1. Health Check
`GET /api/health`

**Response:**
```json
{
  "status": "healthy",
  "service": "DepthWizard API",
  "version": "1.0.0",
  "isro_problem": "SIH26175",
  "capabilities": {
    "monocular_depth": true,
    "geotiff_processing": true,
    "dem_alignment": true,
    "huber_calibration": true,
    "mesh_generation": true
  }
}
```

---

### 2. List Demo Datasets
`GET /api/demo/datasets`

**Response:**
```json
{
  "datasets": [
    {
      "id": "himalaya_mountain",
      "name": "Himalayan Ridge & Valley (Georeferenced GeoTIFF)",
      "description": "Satellite optical RGB tile (EPSG:32643) with matched SRTM 30m reference DEM.",
      "image_path": "data/demo/himalaya_optical.tif",
      "dem_path": "data/demo/himalaya_srtm_dem.tif",
      "is_georeferenced": true
    }
  ]
}
```

---

### 3. Upload File
`POST /api/upload`
- Content-Type: `multipart/form-data`
- Body: `file: <binary_data>`

**Response:**
```json
{
  "file_id": "a1b2c3d4",
  "file_path": "data/temporary/a1b2c3d4_satellite.tif",
  "filename": "satellite.tif",
  "metadata": {
    "is_georeferenced": true,
    "crs": "EPSG:32643",
    "width": 512,
    "height": 512,
    "bounds": { "left": 450000.0, "bottom": 3394880.0, "right": 455120.0, "top": 3400000.0 },
    "gsd": 10.0
  }
}
```

---

### 4. Process Pipeline
`POST /api/process`

**Request Body:**
```json
{
  "image_path": "data/demo/himalaya_optical.tif",
  "dem_path": "data/demo/himalaya_srtm_dem.tif",
  "mesh_resolution": 128,
  "height_exaggeration": 1.2
}
```

**Response:**
```json
{
  "task_id": "7f8a9b0c",
  "status": "success",
  "is_georeferenced": true,
  "is_absolute": true,
  "elevation_unit": "meters",
  "calibration_metrics": {
    "scale": 1584.21,
    "offset": 862.14,
    "mae_meters": 2.14,
    "rmse_meters": 3.21,
    "pearson_r": 0.965,
    "r2_score": 0.932
  },
  "statistics": {
    "min_elevation": 850.0,
    "max_elevation": 2450.0,
    "mean_elevation": 1520.0
  },
  "urls": {
    "texture": "/outputs/7f8a9b0c/texture.png",
    "relative_depth": "/outputs/7f8a9b0c/relative_depth.png",
    "dsm_preview": "/outputs/7f8a9b0c/dsm_preview.png",
    "geotiff_dsm": "/outputs/7f8a9b0c/dsm_metric.tif",
    "obj_mesh": "/outputs/7f8a9b0c/terrain.obj",
    "report_json": "/outputs/7f8a9b0c/report.json"
  }
}
```
