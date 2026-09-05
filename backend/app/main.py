# backend/app/main.py
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from backend.app.config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, OUTPUTS_DIR, TEMP_DIR, DEMO_MODE
from backend.app.api.routes_upload import router as upload_router
from backend.app.api.routes_process import router as process_router
from backend.app.api.routes_analysis import router as analysis_router
from backend.app.api.routes_demo import router as demo_router
from backend.app.api.routes_geo import router as geo_router
from backend.app.api.routes_img2d3d import router as img2d3d_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("depthwizard")

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# CORS middleware for friendly local hostname & cross-origin connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",
        "http://depthwizard.localhost:8000",
        "http://depthwizard.localhost",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://depthwizard.localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs directory for static texture and preview serving
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

# Register API Routers
app.include_router(upload_router)
app.include_router(process_router)
app.include_router(analysis_router)
app.include_router(demo_router)
app.include_router(geo_router)
app.include_router(img2d3d_router)


@app.get("/api/health")
async def health_check():
    """Backend service health and subsystem status check."""
    # Fetch current model status
    try:
        from backend.app.ml.model_manager import ModelManager
        model = ModelManager.get_instance().get_depth_model()
        model_status = model.get_metadata()
    except Exception:
        model_status = {"model_name": "unknown", "is_fallback": True}

    return {
        "status": "healthy",
        "service": "DepthWizard API",
        "version": APP_VERSION,
        "isro_problem": "SIH26175",
        "demo_mode": DEMO_MODE,
        "local_url": "http://depthwizard.localhost:8000",
        "depth_model": model_status,
        "capabilities": {
            "monocular_depth": True,
            "geotiff_processing": True,
            "dem_alignment": True,
            "huber_calibration": True,
            "mesh_generation": True,
            "global_map_discovery": True,
            "3d_buildings": True
        }
    }

@app.on_event("startup")
async def startup_event():
    """Startup routine: pre-warms demo cache if DEMO_MODE is active."""
    if DEMO_MODE:
        logger.info("DEMO_MODE=True: Pre-warming curated demo locations to disk...")
        try:
            from backend.app.api.routes_demo import prewarm_demo_cache
            prewarm_demo_cache()
        except Exception as e:
            logger.error("Failed to pre-warm demo cache at startup: %s", str(e))

# Mount frontend static app at root
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n=============================================================")
    print("  🚀 DEPTHWIZARD SERVER RUNNING")
    print("  🌍 Open in Browser: http://depthwizard.localhost:8000")
    print("  🔗 Alternative URL: http://127.0.0.1:8000")
    print("=============================================================\n")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)


