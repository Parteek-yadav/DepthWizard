# backend/app/ml/ai_supervisor.py
import logging
import os
import json
import base64
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional
import numpy as np
from PIL import Image
import io
from backend.app.config import DEMO_MODE

logger = logging.getLogger(__name__)

class ReconstructionSupervisor:
    """
    AI-Assisted Reconstruction Supervisor using OpenRouter Free Models Router (openrouter/free).
    
    The LLM is NOT a geometry engine; it NEVER invents coordinates or fake geometry.
    It analyzes scene complexity, evaluates depth quality, inspects render previews,
    and returns strict structured JSON recommendations to guide deterministic reconstruction.
    
    If the API key is missing or the service is offline, it gracefully falls back
    to deterministic rule-based decisions.
    """

    @staticmethod
    def get_api_key() -> Optional[str]:
        return os.getenv("OPENROUTER_API_KEY", "").strip() or None

    @staticmethod
    def analyze_reconstruction_context(
        scene_type: str,
        geographic_bounds: Optional[Dict[str, float]],
        dimensions_meters: Optional[Dict[str, float]],
        terrain_stats: Dict[str, float],
        depth_stats: Optional[Dict[str, float]] = None,
        building_count: int = 0,
        has_dem: bool = True
    ) -> Dict[str, Any]:
        """
        Supervises the reconstruction parameters based on geographic and depth telemetry.
        Returns validated structured decision JSON.
        """
        # Default deterministic baseline
        relief = terrain_stats.get("max_meters", 100.0) - terrain_stats.get("min_meters", 0.0)
        width_m = dimensions_meters.get("width", 1000.0) if dimensions_meters else 1000.0
        
        # Rule-based deterministic foundation
        det_mesh_res = 128
        if width_m < 600.0:
            det_mesh_res = 256
        elif width_m > 4000.0:
            det_mesh_res = 128

        det_exaggeration = 1.0
        if relief < 25.0:
            det_exaggeration = 1.4 # Gentle enhancement for ultra-flat plains
        elif relief > 400.0:
            det_exaggeration = 1.0 # True 1:1 scale for rugged mountains

        confidence = "HIGH" if (has_dem and building_count > 0) else ("MEDIUM" if has_dem else "LOW")

        baseline_decision = {
            "scene_type": scene_type,
            "terrain_complexity": round(min(1.0, relief / 300.0), 2),
            "urban_density": round(min(1.0, building_count / 80.0), 2),
            "recommended_terrain_lod": "HIGH" if relief > 80.0 else "MEDIUM",
            "recommended_building_lod": "DETAILED" if building_count < 100 else "SIMPLIFIED",
            "recommended_mesh_resolution": det_mesh_res,
            "recommended_height_exaggeration": det_exaggeration,
            "recommended_camera_altitude_meters": round(max(width_m * 0.45, 120.0), 1),
            "data_confidence": confidence,
            "supervisor_mode": "DETERMINISTIC_RULE_BASED",
            "detected_visual_problems": [],
            "recommended_actions": [
                "Preserve authentic 1:1 metric scale",
                "Extrude real OpenStreetMap vector footprints with terrain base clamping",
                "Apply area-weighted smooth normal vectors"
            ]
        }

        # In DEMO_MODE, bypass OpenRouter network call completely for deterministic consistency
        if DEMO_MODE:
            logger.info("DEMO_MODE=True: Skipping OpenRouter network call and returning deterministic supervisor decision.")
            return baseline_decision

        api_key = ReconstructionSupervisor.get_api_key()
        if not api_key:
            logger.info("OPENROUTER_API_KEY not set. Using authoritative deterministic supervisor.")
            return baseline_decision

        # Query OpenRouter Free Router
        prompt = f"""You are the AI Reconstruction Supervisor for DepthWizard (ISRO SIH26175 Geospatial 3D Engine).
Analyze this reconstruction metadata and output STRICT JSON only (no markdown, no backticks).

Metadata:
- Scene Type: {scene_type}
- Geographic Width: {width_m} meters
- Elevation Relief: {relief} meters (Min: {terrain_stats.get('min_meters')}, Max: {terrain_stats.get('max_meters')})
- Building Count: {building_count}
- Reference DEM Available: {has_dem}
- Depth Stats: {json.dumps(depth_stats or {})}

Respond in EXACT JSON format with these keys:
{{
  "scene_type": "{scene_type}",
  "terrain_complexity": float (0.0 to 1.0),
  "urban_density": float (0.0 to 1.0),
  "recommended_terrain_lod": "ULTRA" | "HIGH" | "MEDIUM" | "LOW",
  "recommended_building_lod": "DETAILED" | "BALANCED" | "SIMPLIFIED",
  "recommended_mesh_resolution": 64 | 128 | 256,
  "recommended_height_exaggeration": float (0.5 to 2.0),
  "recommended_camera_altitude_meters": float,
  "data_confidence": "HIGH" | "MEDIUM" | "LOW",
  "detected_visual_problems": list of strings,
  "recommended_actions": list of strings
}}"""

        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {
                "model": "openrouter/free",
                "messages": [
                    {"role": "system", "content": "You are a geospatial 3D reconstruction AI supervisor. Output strict JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 400
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://depthwizard.localhost:8000",
                    "X-Title": "DepthWizard-ISRO-SIH26175"
                }
            )
            with urllib.request.urlopen(req, timeout=3.5) as res:
                if res.status == 200:
                    resp_data = json.loads(res.read().decode("utf-8"))
                    content = resp_data["choices"][0]["message"]["content"].strip()
                    # Clean markdown wrappers if any
                    if content.startswith("```"):
                        content = content.split("\n", 1)[1]
                        if content.endswith("```"):
                            content = content.rsplit("\n", 1)[0]
                    parsed = json.loads(content)
                    parsed["supervisor_mode"] = "AI_OPENROUTER_FREE"
                    logger.info("AI Reconstruction Supervisor response received successfully.")
                    return parsed
        except Exception as e:
            logger.debug("OpenRouter free router query skipped / fallback: %s", str(e))

        return baseline_decision

    @staticmethod
    def assess_depth_quality(depth_array: np.ndarray) -> Dict[str, Any]:
        """
        Computes mathematical depth map statistics & quality metrics to detect noisy depth,
        flat plateaus, or holes prior to 3D surface meshing.
        """
        valid_mask = ~np.isnan(depth_array) & ~np.isinf(depth_array)
        valid_vals = depth_array[valid_mask]

        if len(valid_vals) == 0:
            return {"status": "error", "message": "Depth array contains no valid pixels"}

        min_val = float(np.min(valid_vals))
        max_val = float(np.max(valid_vals))
        mean_val = float(np.mean(valid_vals))
        std_val = float(np.std(valid_vals))
        median_val = float(np.median(valid_vals))
        p5, p95 = float(np.percentile(valid_vals, 5)), float(np.percentile(valid_vals, 95))
        
        # Edge gradient energy
        gy, gx = np.gradient(depth_array)
        edge_energy = float(np.mean(np.sqrt(gx**2 + gy**2)))
        invalid_pct = float((1.0 - (np.sum(valid_mask) / depth_array.size)) * 100.0)

        # Quality scoring
        quality_score = 1.0
        warnings = []

        if std_val < 1e-4:
            quality_score -= 0.6
            warnings.append("Depth map is completely flat / lack of contrast")
        if invalid_pct > 5.0:
            quality_score -= 0.3
            warnings.append(f"{invalid_pct:.1f}% invalid pixels detected")
        if edge_energy < 0.001:
            warnings.append("Low high-frequency structural detail")

        return {
            "min": round(min_val, 4),
            "max": round(max_val, 4),
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "median": round(median_val, 4),
            "p5": round(p5, 4),
            "p95": round(p95, 4),
            "edge_energy": round(edge_energy, 4),
            "invalid_pixel_percentage": round(invalid_pct, 2),
            "quality_score": round(max(0.1, quality_score), 2),
            "warnings": warnings,
            "is_suitable_for_mesh": quality_score >= 0.4
        }
