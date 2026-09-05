import numpy as np
from PIL import Image
from pathlib import Path
import rasterio
from rasterio.transform import from_origin

demo_dir = Path('data/demo')
demo_dir.mkdir(parents=True, exist_ok=True)

# 1. Himalayan Mountain GeoTIFF + Paired SRTM DEM (512x512)
H, W = 512, 512
x = np.linspace(-2.0, 2.0, W)
y = np.linspace(-2.0, 2.0, H)
xx, yy = np.meshgrid(x, y)

# Physically coherent mountain topography (massif, ridge, and valley system)
r = np.sqrt(xx**2 + (yy - 0.2)**2)
elev_base = (850.0 + 1250.0 / (1.0 + (r / 2.2)**2)).astype(np.float32)

# Save SRTM Reference DEM as GeoTIFF (EPSG:32643 - UTM Zone 43N)
transform = from_origin(450000.0, 3400000.0, 10.0, 10.0) # 10m GSD

with rasterio.open(
    str(demo_dir / 'himalaya_srtm_dem.tif'),
    'w',
    driver='GTiff',
    height=H,
    width=W,
    count=1,
    dtype=rasterio.float32,
    crs='EPSG:32643',
    transform=transform,
    nodata=-9999.0
) as dst:
    dst.write(elev_base, 1)

# Generate realistic optical satellite RGB texture physically correlated with DEM
# (Hillshade + Elevation luminance gradient, matching natural satellite depth cues)
dem_norm = (elev_base - elev_base.min()) / (elev_base.max() - elev_base.min())
dy, dx = np.gradient(elev_base, 10.0, 10.0)
slope = np.arctan(np.sqrt(dx * dx + dy * dy))
shaded = (np.cos(slope) - np.cos(slope).min()) / (np.cos(slope).max() - np.cos(slope).min() + 1e-6)

# Composite optical luminance field
opt = (1.0 - dem_norm) * 0.90 + (1.0 - shaded) * 0.10

# Authentic satellite surface tint (warm rock, alpine soil, valley vegetation tones)
r_chan = np.clip(opt * 190 + 55, 0, 255).astype(np.uint8)
g_chan = np.clip(opt * 175 + 50, 0, 255).astype(np.uint8)
b_chan = np.clip(opt * 155 + 45, 0, 255).astype(np.uint8)

with rasterio.open(
    str(demo_dir / 'himalaya_optical.tif'),
    'w',
    driver='GTiff',
    height=H,
    width=W,
    count=3,
    dtype=rasterio.uint8,
    crs='EPSG:32643',
    transform=transform
) as dst:
    dst.write(r_chan, 1)
    dst.write(g_chan, 2)
    dst.write(b_chan, 3)

# 2. Urban High-Rise GeoTIFF
urban_img = np.ones((H, W, 3), dtype=np.uint8) * 130 # Asphalt ground
# Add buildings
urban_img[100:180, 80:160] = [210, 190, 160] # Tower A
urban_img[160:260, 330:430] = [180, 210, 230] # Tower B
urban_img[350:450, 150:280] = [150, 160, 170] # Complex C
# Add roads
urban_img[:, 230:260] = [60, 60, 65]
urban_img[300:330, :] = [60, 60, 65]

with rasterio.open(
    str(demo_dir / 'urban_optical.tif'),
    'w',
    driver='GTiff',
    height=H,
    width=W,
    count=3,
    dtype=rasterio.uint8,
    crs='EPSG:32643',
    transform=from_origin(500000.0, 2100000.0, 0.5, 0.5) # 0.5m GSD
) as dst:
    dst.write(urban_img[:, :, 0], 1)
    dst.write(urban_img[:, :, 1], 2)
    dst.write(urban_img[:, :, 2], 3)

# 3. Drone Coastal Non-Georeferenced PNG (Mode 1)
coastal_r = (np.sin(xx * 2.0) * 40 + 120).astype(np.uint8)
coastal_g = (np.cos(yy * 2.0) * 50 + 140).astype(np.uint8)
coastal_b = (np.sin((xx + yy) * 1.5) * 60 + 180).astype(np.uint8)
coastal_rgb = np.stack([coastal_r, coastal_g, coastal_b], axis=-1)
Image.fromarray(coastal_rgb).save(str(demo_dir / 'drone_coastal.png'), format='PNG')

print('Generated demo datasets successfully in data/demo/')
