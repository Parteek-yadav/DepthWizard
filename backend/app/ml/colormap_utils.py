# backend/app/ml/colormap_utils.py
import numpy as np
from PIL import Image

def apply_scientific_colormap(data_2d: np.ndarray, colormap_name: str = "turbo") -> np.ndarray:
    """
    Applies scientific elevation/depth colormap to 2D normalized [0, 1] array.
    Returns RGB uint8 image (H, W, 3).
    """
    clipped = np.clip(data_2d, 0.0, 1.0)
    
    # 256-step perceptual palettes
    if colormap_name == "turbo":
        # Smooth perceptual rainbow Turbo
        r = np.sin(np.pi * (clipped - 0.25)) * 0.5 + 0.5
        g = np.sin(np.pi * (clipped - 0.5)) * 0.5 + 0.5
        b = np.sin(np.pi * (clipped - 0.75)) * 0.5 + 0.5
        # Refine polynomial Turbo curve
        k = clipped
        r = 0.1357 + k * (4.5874 + k * (-42.3082 + k * (130.543 + k * (-150.561 + k * 58.13))))
        g = 0.0914 + k * (2.1941 + k * (4.8061 + k * (-14.0195 + k * (4.2169 + k * 2.88))))
        b = 0.1066 + k * (12.5593 + k * (-90.6877 + k * (229.016 + k * (-245.549 + k * 94.67))))
        rgb = np.stack([r, g, b], axis=-1)
    elif colormap_name == "viridis":
        # Viridis standard
        r = np.clip(0.26 + 0.74 * (clipped ** 1.5), 0, 1)
        g = np.clip(0.18 + 0.82 * (clipped ** 0.8), 0, 1)
        b = np.clip(0.33 + 0.67 * (1.0 - clipped), 0, 1)
        rgb = np.stack([r, g, b], axis=-1)
    elif colormap_name == "terrain":
        # Topographic Terrain (Blue ocean/valley -> Green vegetation -> Brown mountain -> White snow)
        r = np.where(clipped < 0.2, 0.1, np.where(clipped < 0.6, 0.2 + (clipped - 0.2) * 1.5, np.where(clipped < 0.85, 0.8, 1.0)))
        g = np.where(clipped < 0.2, 0.3 + clipped * 2.0, np.where(clipped < 0.6, 0.7 - (clipped - 0.2) * 0.5, np.where(clipped < 0.85, 0.5, 1.0)))
        b = np.where(clipped < 0.2, 0.8 - clipped * 2.0, np.where(clipped < 0.6, 0.2, np.where(clipped < 0.85, 0.2, 1.0)))
        rgb = np.stack([r, g, b], axis=-1)
    else: # grayscale
        rgb = np.stack([clipped, clipped, clipped], axis=-1)
        
    rgb_uint8 = np.clip(rgb * 255.0, 0, 255).astype(np.uint8)
    return rgb_uint8

def save_colormap_image(data_2d: np.ndarray, output_path: str, colormap_name: str = "turbo"):
    rgb = apply_scientific_colormap(data_2d, colormap_name)
    img = Image.fromarray(rgb)
    img.save(output_path, format="PNG")
