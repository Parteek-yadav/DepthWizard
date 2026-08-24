# backend/app/geospatial/dem_aligner.py
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import numpy as np
from PIL import Image
from scipy.ndimage import zoom

logger = logging.getLogger(__name__)

class DEMAligner:
    """Loads, reprojects, and resamples reference elevation DEM rasters (SRTM/COP30)."""

    @staticmethod
    def load_and_align_dem(dem_path: str, target_shape: Tuple[int, int], target_bounds: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        Loads reference DEM and resamples it to target_shape (H, W).
        Returns float32 2D array of reference elevations in meters.
        """
        target_h, target_w = target_shape
        try:
            import rasterio
            from rasterio.enums import Resampling
            from rasterio.warp import reproject

            with rasterio.open(dem_path) as src:
                dem_data = src.read(1).astype(np.float32)
                # Handle nodata
                if src.nodata is not None:
                    dem_data[dem_data == src.nodata] = np.nan

                # If dimensions already match
                if dem_data.shape == target_shape:
                    # Fill any nan with median
                    valid_mask = ~np.isnan(dem_data)
                    if valid_mask.any():
                        dem_data[~valid_mask] = np.nanmedian(dem_data)
                    return dem_data

                # Resample DEM to target shape using spline/bilinear
                zoom_h = target_h / dem_data.shape[0]
                zoom_w = target_w / dem_data.shape[1]
                resampled = zoom(dem_data, (zoom_h, zoom_w), order=1)
                return resampled[:target_h, :target_w].astype(np.float32)
        except Exception as e:
            logger.warning(f"DEM aligner fallback loading: {e}")
            img = Image.open(dem_path).resize((target_w, target_h), Image.BILINEAR)
            arr = np.array(img, dtype=np.float32)
            if arr.ndim == 3:
                arr = arr[:, :, 0]
            return arr
