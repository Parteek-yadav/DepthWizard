# backend/app/processing/exporter.py
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
from PIL import Image

from backend.app.ml.colormap_utils import save_colormap_image

logger = logging.getLogger(__name__)

class ResultExporter:
    """Handles serialization of calibrated elevation rasters, 3D meshes, and geospatial metadata."""

    @staticmethod
    def export_geotiff_dsm(
        elevation_data: np.ndarray,
        output_path: str,
        spatial_meta: Dict[str, Any]
    ) -> bool:
        """Writes GeoTIFF DSM with proper CRS, bounds, and affine transform tags."""
        try:
            import rasterio
            from rasterio.transform import Affine

            H, W = elevation_data.shape
            crs = spatial_meta.get("crs")
            transform_list = spatial_meta.get("transform")

            if transform_list and len(transform_list) >= 6:
                transform = Affine(*transform_list[:6])
            else:
                transform = Affine.identity()

            with rasterio.open(
                output_path,
                'w',
                driver='GTiff',
                height=H,
                width=W,
                count=1,
                dtype=rasterio.float32,
                crs=crs,
                transform=transform,
                nodata=-9999.0
            ) as dst:
                dst.write(elevation_data.astype(np.float32), 1)
            return True
        except Exception as e:
            logger.error(f"Error exporting GeoTIFF: {e}")
            return False

    @staticmethod
    def export_png_preview(
        raster_2d: np.ndarray,
        output_path: str,
        colormap: str = "turbo"
    ):
        """Normalizes raster to [0, 1] and saves colored PNG."""
        rmin, rmax = np.nanmin(raster_2d), np.nanmax(raster_2d)
        if rmax > rmin:
            norm = (raster_2d - rmin) / (rmax - rmin)
        else:
            norm = np.zeros_like(raster_2d)
        save_colormap_image(norm, output_path, colormap_name=colormap)

    @staticmethod
    def export_analysis_report(
        report_data: Dict[str, Any],
        output_path: str
    ):
        """Saves detailed JSON analysis report."""
        with open(output_path, "w") as f:
            json.dump(report_data, f, indent=2)
