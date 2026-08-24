# backend/app/geospatial/calibrator.py
import logging
from typing import Any, Dict, Optional, Tuple
import numpy as np
from sklearn.linear_model import HuberRegressor, RANSACRegressor, LinearRegression
from scipy.stats import pearsonr

logger = logging.getLogger(__name__)

class ElevationCalibrator:
    """
    Calibrates monocular relative depth field D_rel into absolute physical metric elevation:
        Z_metric(x, y) = scale * D_rel(x, y) + offset
    Using robust M-estimation (Huber Regression) against reference DEM samples or GCPs.
    """

    @staticmethod
    def calibrate_from_dem(
        relative_depth: np.ndarray,
        reference_dem: np.ndarray,
        max_samples: int = 10000,
        val_split: float = 0.2
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calibrates full 2D relative depth raster against aligned reference DEM.
        Returns:
            calibrated_dsm: 2D np.ndarray (H, W) in meters.
            metrics: Dict containing scale, offset, MAE, RMSE, Pearson r, R², and diagnostics.
        """
        H, W = relative_depth.shape
        d_flat = relative_depth.flatten()
        z_flat = reference_dem.flatten()

        # Valid mask (non-NaN and finite)
        valid_mask = (~np.isnan(d_flat)) & (~np.isnan(z_flat)) & (np.isfinite(d_flat)) & (np.isfinite(z_flat))
        d_valid = d_flat[valid_mask]
        z_valid = z_flat[valid_mask]

        if len(d_valid) < 10:
            raise ValueError(f"Insufficient valid spatial samples for calibration: {len(d_valid)} found.")

        # Subsample for efficient and unbiased regression
        total_valid = len(d_valid)
        if total_valid > max_samples:
            indices = np.random.RandomState(42).choice(total_valid, size=max_samples, replace=False)
            d_sampled = d_valid[indices]
            z_sampled = z_valid[indices]
        else:
            d_sampled = d_valid
            z_sampled = z_valid

        # Split train / validation
        num_val = int(len(d_sampled) * val_split)
        train_idx = np.arange(len(d_sampled) - num_val)
        val_idx = np.arange(len(d_sampled) - num_val, len(d_sampled))

        d_train, z_train = d_sampled[train_idx].reshape(-1, 1), z_sampled[train_idx]
        d_val, z_val = d_sampled[val_idx], z_sampled[val_idx]

        # Fit Robust Huber Regressor
        huber = HuberRegressor(epsilon=1.35, max_iter=200)
        huber.fit(d_train, z_train)

        scale = float(huber.coef_[0])
        offset = float(huber.intercept_)

        # Compute metric DSM
        calibrated_dsm = (scale * relative_depth + offset).astype(np.float32)

        # Validation metrics on held-out test points
        z_pred_val = scale * d_val + offset
        residuals = z_val - z_pred_val
        mae = float(np.mean(np.abs(residuals)))
        rmse = float(np.sqrt(np.mean(residuals ** 2)))
        
        # Pearson correlation
        if len(d_val) > 2 and np.std(z_pred_val) > 1e-6 and np.std(z_val) > 1e-6:
            r_val, _ = pearsonr(z_pred_val, z_val)
            r_score = float(r_val)
        else:
            r_score = 0.0

        # R² score
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((z_val - np.mean(z_val)) ** 2)
        r2 = float(1.0 - (ss_res / (ss_tot + 1e-8))) if ss_tot > 1e-8 else 0.0

        metrics = {
            "scale": scale,
            "offset": offset,
            "mae_meters": round(mae, 3),
            "rmse_meters": round(rmse, 3),
            "pearson_r": round(r_score, 4),
            "r2_score": round(r2, 4),
            "sample_count": len(d_sampled),
            "validation_sample_count": len(d_val),
            "min_elevation_m": round(float(np.nanmin(calibrated_dsm)), 2),
            "max_elevation_m": round(float(np.nanmax(calibrated_dsm)), 2),
            "mean_elevation_m": round(float(np.nanmean(calibrated_dsm)), 2),
            "method": "Robust Huber M-Estimation (Iteratively Reweighted Least Squares)"
        }

        return calibrated_dsm, metrics

    @staticmethod
    def calibrate_from_gcps(
        relative_depth: np.ndarray,
        d_samples: np.ndarray,
        z_samples: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Calibrates using discrete Ground Control Points.
        """
        if len(d_samples) < 2:
            raise ValueError("At least 2 Ground Control Points are required for affine elevation calibration.")

        if len(d_samples) >= 4:
            reg = HuberRegressor(epsilon=1.35, max_iter=200)
            reg.fit(d_samples.reshape(-1, 1), z_samples)
            scale = float(reg.coef_[0])
            offset = float(reg.intercept_)
        else:
            reg = LinearRegression()
            reg.fit(d_samples.reshape(-1, 1), z_samples)
            scale = float(reg.coef_[0])
            offset = float(reg.intercept_)

        calibrated_dsm = (scale * relative_depth + offset).astype(np.float32)

        z_pred = scale * d_samples + offset
        residuals = z_samples - z_pred
        mae = float(np.mean(np.abs(residuals)))
        rmse = float(np.sqrt(np.mean(residuals ** 2)))

        metrics = {
            "scale": scale,
            "offset": offset,
            "mae_meters": round(mae, 3),
            "rmse_meters": round(rmse, 3),
            "gcp_count": len(d_samples),
            "min_elevation_m": round(float(np.nanmin(calibrated_dsm)), 2),
            "max_elevation_m": round(float(np.nanmax(calibrated_dsm)), 2),
            "mean_elevation_m": round(float(np.nanmean(calibrated_dsm)), 2),
            "method": "Ground Control Point (GCP) Robust Regression"
        }

        return calibrated_dsm, metrics
