// frontend/src/services/api.ts
import { ProcessResponse, DemoDataset } from '../types';

export async function checkHealth(): Promise<any> {
  const res = await fetch('/api/health');
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function fetchDemoDatasets(): Promise<{ datasets: DemoDataset[] }> {
  const res = await fetch('/api/demo/datasets');
  if (!res.ok) throw new Error('Failed to fetch demo datasets');
  return res.json();
}

export async function uploadFile(file: File): Promise<{ file_id: string; file_path: string; filename: string; metadata: any }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch('/api/upload', {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('File upload failed');
  return res.json();
}

export async function runProcessing(payload: {
  image_path: string;
  dem_path?: string;
  gcps?: any[];
  mesh_resolution?: number;
  height_exaggeration?: number;
}): Promise<ProcessResponse> {
  const res = await fetch('/api/process', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Processing error' }));
    throw new Error(err.detail || 'Processing failed');
  }
  return res.json();
}

export async function measurePoints(payload: {
  task_id: string;
  point_a: [number, number];
  point_b: [number, number];
  z1: number;
  z2: number;
  gsd_meters?: number;
}): Promise<any> {
  const res = await fetch('/api/analysis/measure', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Measurement failed');
  return res.json();
}
