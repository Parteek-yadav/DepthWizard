// frontend/src/types/index.ts
export interface SpatialMetadata {
  is_georeferenced: boolean;
  crs?: string | null;
  width: number;
  height: number;
  bands_count: number;
  bounds?: { left: number; bottom: number; right: number; top: number } | null;
  transform?: number[] | null;
  gsd?: number | null;
  nodata?: number | null;
  filename: string;
}

export interface CalibrationMetrics {
  scale: number;
  offset: number;
  mae_meters: number;
  rmse_meters: number;
  pearson_r: number;
  r2_score: number;
  sample_count?: number;
  validation_sample_count?: number;
  gcp_count?: number;
  min_elevation_m: number;
  max_elevation_m: number;
  mean_elevation_m: number;
  method: string;
}

export interface MeshData {
  vertices: number[];
  normals: number[];
  uvs: number[];
  indices: number[];
  grid_size: [number, number];
  z_min_meters: number;
  z_max_meters: number;
  vertex_count: number;
  face_count: number;
}

export interface SummaryStats {
  min_elevation: number;
  max_elevation: number;
  mean_elevation: number;
  std_elevation: number;
  elevation_unit: string;
  dimensions: { width: number; height: number };
  is_georeferenced: boolean;
  is_absolute: boolean;
}

export interface HistogramBin {
  bin_start: number;
  bin_end: number;
  count: number;
}

export interface ProcessResponse {
  task_id: string;
  status: string;
  is_georeferenced: boolean;
  is_absolute: boolean;
  elevation_unit: string;
  spatial_metadata: SpatialMetadata;
  model_metadata: {
    model_name: string;
    backbone: string;
    source: string;
    device: string;
    is_fallback: boolean;
    output_type: string;
  };
  calibration_metrics?: CalibrationMetrics | null;
  statistics: SummaryStats;
  histogram: HistogramBin[];
  mesh: MeshData;
  urls: {
    texture: string;
    relative_depth: string;
    dsm_preview: string;
    geotiff_dsm?: string | null;
    obj_mesh: string;
    report_json: string;
  };
}

export interface DemoDataset {
  id: string;
  name: string;
  description: string;
  image_path: string;
  dem_path?: string;
  is_georeferenced: boolean;
  expected_crs?: string;
  elevation_range?: string;
  gcps?: any[];
}
