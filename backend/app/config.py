# backend/app/config.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Load local .env file if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DEMO_DATA_DIR = DATA_DIR / "demo"
OUTPUTS_DIR = DATA_DIR / "outputs"
TEMP_DIR = DATA_DIR / "temporary"
CACHE_DIR = BACKEND_DIR / "cache"

# Ensure all vital data directories exist
for directory in [DATA_DIR, DEMO_DATA_DIR, OUTPUTS_DIR, TEMP_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Config
APP_TITLE = "DepthWizard API"
APP_DESCRIPTION = "Single-View Height Estimation and 3D Flythrough (ISRO SIH26175)"
APP_VERSION = "1.0.0"

# OpenRouter Free Router Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = "openrouter/free"

# Processing limits
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "100"))
DEFAULT_MESH_RESOLUTION = int(os.getenv("DEFAULT_MESH_RESOLUTION", "256"))
MAX_MESH_RESOLUTION = 512
DEVICE = os.getenv("DEVICE", "auto") # auto, cuda, cpu

# Presentation Demo Mode Flag
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
