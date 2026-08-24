import numpy as np
from PIL import Image
from pathlib import Path
import rasterio
from rasterio.transform import from_origin

demo_dir = Path('data/demo')
demo_dir.mkdir(parents=True, exist_ok=True)

# 1. Himalayan Mountain GeoTIFF + Paired SRTM DEM (512x512)
H, W = 512, 512
x = np.linspace(-3, 3, W)
y = np.linspace(-3, 3, H)
xx, yy = np.meshgrid(x, y)

# Topographic elevation function (Mountain peaks, valley, ridges)
elev_base = (
    850.0 + 
    600.0 * np.exp(-((xx - 0.5)**2 + (yy - 0.5)**2) / 1.5) +
    900.0 * np.exp(-((xx + 1.2)**2 + (yy + 0.8)**2) / 2.0) +
    450.0 * np.cos(xx * 2.5) * np.sin(yy * 2.5) +
    200.0 * np.sin(xx * 5.0)
)
elev_base = np.clip(elev_base, 850.0, 2450.0).astype(np.float32)

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

# Generate realistic optical satellite RGB texture corresponding to terrain
norm_elev = (elev_base - 850.0) / 1600.0
# Green valleys -> Brown rocks -> White snow peaks
r_chan = np.clip(np.where(norm_elev < 0.3, 70 + norm_elev * 100, np.where(norm_elev < 0.7, 140 + (norm_elev - 0.3) * 150, 220 + (norm_elev - 0.7) * 100)), 0, 255)
g_chan = np.clip(np.where(norm_elev < 0.3, 130 - norm_elev * 50, np.where(norm_elev < 0.7, 110 - (norm_elev - 0.3) * 40, 225 + (norm_elev - 0.7) * 80)), 0, 255)
b_chan = np.clip(np.where(norm_elev < 0.3, 60 + norm_elev * 20, np.where(norm_elev < 0.7, 75 + (norm_elev - 0.3) * 30, 240 + (norm_elev - 0.7) * 40)), 0, 255)

# Add subtle satellite noise & shadows
shading = np.gradient(elev_base, axis=1) * 0.1
r_chan = np.clip(r_chan + shading, 0, 255).astype(np.uint8)
g_chan = np.clip(g_chan + shading, 0, 255).astype(np.uint8)
b_chan = np.clip(b_chan + shading, 0, 255).astype(np.uint8)

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
