# backend/tests/test_mesh_generation.py
import pytest
import numpy as np
from backend.app.processing.mesh_generator import MeshGenerator

def test_terrain_mesh_generation():
    elev = np.ones((64, 64), dtype=np.float32) * 500.0
    elev[20:40, 20:40] = 800.0

    mesh_data = MeshGenerator.generate_terrain_mesh(elev, target_grid_size=32)

    assert mesh_data["vertex_count"] == 32 * 32
    assert len(mesh_data["vertices"]) == 32 * 32 * 3
    assert len(mesh_data["uvs"]) == 32 * 32 * 2
    assert len(mesh_data["normals"]) == 32 * 32 * 3
    assert mesh_data["face_count"] == (31 * 31 * 2)

def test_obj_export(tmp_path):
    elev = np.ones((16, 16), dtype=np.float32) * 100.0
    mesh_data = MeshGenerator.generate_terrain_mesh(elev, target_grid_size=8)
    obj_file = tmp_path / "test_terrain.obj"
    MeshGenerator.export_obj(mesh_data, str(obj_file))
    assert obj_file.exists()
    assert obj_file.stat().st_size > 0
