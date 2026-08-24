# backend/app/geospatial/geotiff_handler.py
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class GeoTIFFHandler:
    """Reads and extracts metadata, CRS, affine transforms, and photometric bands from GeoTIFF rasters."""

    @staticmethod
    def inspect_raster(file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Raster file not found: {file_path}")

        # Check if file is GeoTIFF
        is_geotiff = False
        crs_str = None
        bounds = None
        transform_matrix = None
        gsd = None
        nodata = None
        width, height, bands_count = 0, 0, 0

        try:
            import rasterio
            with rasterio.open(file_path) as src:
                is_geotiff = src.crs is not None
                width, height = src.width, src.height
                bands_count = src.count
                if is_geotiff:
                    crs_str = str(src.crs)
                    b = src.bounds
                    bounds = {
                        "left": float(b.left),
                        "bottom": float(b.bottom),
                        "right": float(b.right),
                        "top": float(b.top)
                    }
                    transform_matrix = [float(x) for x in list(src.transform)[:6]]
                    # Calculate ground sample distance (GSD) in CRS units / meters
                    gsd_x = abs(src.transform[0])
                    gsd_y = abs(src.transform[4])
                    gsd = float((gsd_x + gsd_y) / 2.0)
                    nodata = float(src.nodata) if src.nodata is not None else None
        except Exception as e:
            logger.info(f"Standard raster parser fallback: {e}")
            img = Image.open(file_path)
            width, height = img.size
            bands_count = len(img.getbands())

        return {
            "is_georeferenced": is_geotiff,
            "crs": crs_str,
            "width": width,
            "height": height,
            "bands_count": bands_count,
            "bounds": bounds,
            "transform": transform_matrix,
            "gsd": gsd,
            "nodata": nodata,
            "filename": path.name
        }

    @staticmethod
    def read_rgb(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reads raster and returns RGB uint8 array (H, W, 3) alongside spatial metadata."""
        meta = GeoTIFFHandler.inspect_raster(file_path)
        try:
            import rasterio
            with rasterio.open(file_path) as src:
                if src.count >= 3:
                    r = src.read(1)
                    g = src.read(2)
                    b = src.read(3)
                    rgb = np.stack([r, g, b], axis=-1)
                elif src.count == 1:
                    gray = src.read(1)
                    rgb = np.stack([gray, gray, gray], axis=-1)
                else:
                    arr = src.read()
                    rgb = np.transpose(arr[:3], (1, 2, 0))

                # Normalize to uint8 if float or 16-bit
                if rgb.dtype != np.uint8:
                    rmin, rmax = np.percentile(rgb, 1), np.percentile(rgb, 99)
                    if rmax > rmin:
                        rgb = np.clip((rgb - rmin) / (rmax - rmin) * 255.0, 0, 255).astype(np.uint8)
                    else:
                        rgb = rgb.astype(np.uint8)
                return rgb, meta
        except Exception as e:
            logger.info(f"Fallback reading with PIL: {e}")
            img = Image.open(file_path).convert("RGB")
            return np.array(img, dtype=np.uint8), meta
