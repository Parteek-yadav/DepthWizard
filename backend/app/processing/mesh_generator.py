# backend/app/processing/mesh_generator.py
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from scipy.ndimage import zoom

logger = logging.getLogger(__name__)

class MeshGenerator:
    """
    Continuous height-field triangulated surface mesh generator.
    Preserves exact metric geospatial scale, physical elevation values,
    consistent triangle winding order, and smooth analytical normal vectors.
    """

    @staticmethod
    def generate_terrain_mesh(
        elevation_2d: np.ndarray,
        target_grid_size: int = 128,
        height_exaggeration: float = 1.0,
        spatial_bounds_meters: Optional[Tuple[float, float, float, float]] = None,
        nodata_val: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Constructs a mathematically continuous 3D triangulated TIN surface from a 2D elevation grid.

        Parameters:
            elevation_2d: 2D numpy array of elevation / depth values (H x W)
            target_grid_size: maximum grid dimension for adaptive LOD
            height_exaggeration: vertical display exaggeration multiplier (default 1.0 = true 1:1 metric)
            spatial_bounds_meters: (min_x, min_y, max_x, max_y) in meters relative to scene center.
                                  If None, defaults to symmetric [-50m, +50m] coordinate frame.
            nodata_val: nodata sentinel value to mask invalid samples

        Returns:
            Dictionary containing:
                vertices: [x0, y0, z0, x1, y1, z1, ...]
                normals:  [nx0, ny0, nz0, ...]
                uvs:      [u0, v0, u1, v1, ...]
                indices:  [i0, i1, i2, ...]
                z_min_meters, z_max_meters, z_mean_meters
                bounds_meters: {min_x, max_x, min_y, max_y, min_z, max_z}
                vertex_count, face_count
        """
        raw_elev = np.array(elevation_2d, dtype=np.float32)
        H, W = raw_elev.shape

        # Handle nodata masking
        valid_mask = np.isfinite(raw_elev)
        if nodata_val is not None:
            valid_mask &= (raw_elev != nodata_val)

        if not np.any(valid_mask):
            raw_elev = np.zeros_like(raw_elev)
            valid_mask = np.ones_like(raw_elev, dtype=bool)

        # Replace invalid values with local mean for smooth surface continuity
        valid_mean = float(np.mean(raw_elev[valid_mask]))
        raw_elev[~valid_mask] = valid_mean

        # Determine target grid resolution
        grid_h = min(target_grid_size, H)
        grid_w = min(target_grid_size, W)

        if (H, W) != (grid_h, grid_w):
            zh = grid_h / H
            zw = grid_w / W
            elev_grid = zoom(raw_elev, (zh, zw), order=1).astype(np.float32)
        else:
            elev_grid = raw_elev.copy()

        # Elevation statistics in true physical units (meters)
        z_min = float(np.min(elev_grid))
        z_max = float(np.max(elev_grid))
        z_mean = float(np.mean(elev_grid))
        z_range = max(1e-4, z_max - z_min)

        # Spatial Extents (East-West X, North-South Y) in meters
        if spatial_bounds_meters:
            min_x, min_y, max_x, max_y = spatial_bounds_meters
        else:
            min_x, max_x = -50.0, 50.0
            min_y, max_y = -50.0, 50.0

        x_coords = np.linspace(min_x, max_x, grid_w, dtype=np.float32)
        y_coords = np.linspace(max_y, min_y, grid_h, dtype=np.float32) # North is index 0

        # Physical vertical elevation centered around mean datum for numerical stability
        # In Three.js: X = East-West, Y = Vertical Elevation (Up), Z = South-North
        norm_factor = 1.0
        # If no explicit metric spatial bounds given (e.g. non-georeferenced Mode 1), scale display height proportionally
        if spatial_bounds_meters is None:
            # Map vertical range to proportional terrain relief (~15% of width)
            norm_factor = 15.0 / z_range if z_range > 0 else 1.0

        vertices: List[float] = []
        uvs: List[float] = []

        for i in range(grid_h):
            y_north = float(y_coords[i])
            # Three.js coordinate convention: -Z is North, +Z is South
            vz = float(-y_north)
            v_tex = float(1.0 - (i / (grid_h - 1)))

            for j in range(grid_w):
                vx = float(x_coords[j])
                u_tex = float(j / (grid_w - 1))

                # Vertical height in Three.js units (Y-axis)
                if spatial_bounds_meters:
                    # True metric height relative to mean datum
                    vy = float((elev_grid[i, j] - z_mean) * height_exaggeration)
                else:
                    # Relative normalized height
                    vy = float((elev_grid[i, j] - z_min) * norm_factor * height_exaggeration)

                vertices.extend([vx, vy, vz])
                uvs.extend([u_tex, v_tex])

        # Construct continuous indexed triangle grid (counter-clockwise winding)
        # For each quad (i, j):
        # P00 (top-left)    = i * grid_w + j
        # P10 (top-right)   = i * grid_w + (j + 1)
        # P01 (bottom-left) = (i + 1) * grid_w + j
        # P11 (bottom-right)= (i + 1) * grid_w + (j + 1)
        indices: List[int] = []
        for i in range(grid_h - 1):
            row1 = i * grid_w
            row2 = (i + 1) * grid_w
            for j in range(grid_w - 1):
                p00 = row1 + j
                p10 = row1 + j + 1
                p01 = row2 + j
                p11 = row2 + j + 1

                # Triangle 1: P00 -> P01 -> P10
                indices.extend([p00, p01, p10])
                # Triangle 2: P10 -> P01 -> P11
                indices.extend([p10, p01, p11])

        # Compute smooth analytical surface normals from vertex neighborhood gradients
        normals = MeshGenerator.compute_smooth_normals(vertices, indices)

        v_arr = np.array(vertices, dtype=np.float32).reshape(-1, 3)

        return {
            "vertices": vertices,
            "normals": normals,
            "uvs": uvs,
            "indices": indices,
            "grid_size": [grid_w, grid_h],
            "z_min_meters": round(z_min, 2),
            "z_max_meters": round(z_max, 2),
            "z_mean_meters": round(z_mean, 2),
            "bounds_meters": {
                "min_x": float(np.min(v_arr[:, 0])),
                "max_x": float(np.max(v_arr[:, 0])),
                "min_y": float(np.min(v_arr[:, 1])),
                "max_y": float(np.max(v_arr[:, 1])),
                "min_z": float(np.min(v_arr[:, 2])),
                "max_z": float(np.max(v_arr[:, 2]))
            },
            "vertex_count": len(vertices) // 3,
            "face_count": len(indices) // 3
        }

    @staticmethod
    def compute_smooth_normals(vertices: List[float], indices: List[int]) -> List[float]:
        """
        Computes area-weighted vertex normals for the continuous triangle mesh.
        Ensures lighting reacts naturally to slope gradients and topographic relief.
        """
        num_vertices = len(vertices) // 3
        v_arr = np.array(vertices, dtype=np.float32).reshape(-1, 3)
        normals = np.zeros((num_vertices, 3), dtype=np.float32)

        idx_arr = np.array(indices, dtype=np.int32).reshape(-1, 3)
        p0 = v_arr[idx_arr[:, 0]]
        p1 = v_arr[idx_arr[:, 1]]
        p2 = v_arr[idx_arr[:, 2]]

        edge1 = p1 - p0
        edge2 = p2 - p0
        # Face cross product normals (unnormalized for natural area weighting)
        face_normals = np.cross(edge1, edge2)

        for k in range(3):
            np.add.at(normals, idx_arr[:, k], face_normals)

        # Normalize vertex normals
        norms = np.linalg.norm(normals, axis=1, keepdims=True)
        norms[norms == 0.0] = 1.0
        normals = normals / norms

        return normals.flatten().tolist()

    @staticmethod
    def export_obj(mesh_data: Dict[str, Any], output_path: str):
        """Exports standard Wavefront .OBJ 3D terrain surface file."""
        verts = mesh_data["vertices"]
        uvs = mesh_data["uvs"]
        indices = mesh_data["indices"]
        normals = mesh_data.get("normals", [])

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# DepthWizard 3D Continuous Terrain Mesh (ISRO SIH26175)\n")
            f.write(f"# Vertices: {len(verts)//3}, Triangles: {len(indices)//3}\n")
            
            for i in range(0, len(verts), 3):
                f.write(f"v {verts[i]:.4f} {verts[i+1]:.4f} {verts[i+2]:.4f}\n")
                
            for i in range(0, len(uvs), 2):
                f.write(f"vt {uvs[i]:.4f} {uvs[i+1]:.4f}\n")

            if normals:
                for i in range(0, len(normals), 3):
                    f.write(f"vn {normals[i]:.4f} {normals[i+1]:.4f} {normals[i+2]:.4f}\n")

            has_vn = bool(normals)
            for i in range(0, len(indices), 3):
                i0 = indices[i] + 1
                i1 = indices[i+1] + 1
                i2 = indices[i+2] + 1
                if has_vn:
                    f.write(f"f {i0}/{i0}/{i0} {i1}/{i1}/{i1} {i2}/{i2}/{i2}\n")
                else:
                    f.write(f"f {i0}/{i0} {i1}/{i1} {i2}/{i2}\n")
