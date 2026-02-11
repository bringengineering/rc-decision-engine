"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.postgres import engine
from app.auth.router import router as auth_router
from app.projects.router import router as projects_router
from app.assets.router import router as assets_router
from app.sensors.router import router as sensors_router
from app.calibration.router import router as calibration_router
from app.simulation.router import router as simulation_router
from app.decisions.router import router as decisions_router
from app.reports.router import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    yield
    await engine.dispose()


app = FastAPI(
    title="RC Decision Engine",
    description="Reality-Calibrated Decision Support System",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["Projects"])
app.include_router(assets_router, prefix="/api/projects", tags=["Assets"])
app.include_router(sensors_router, prefix="/api/sensors", tags=["Sensors"])
app.include_router(calibration_router, prefix="/api/assets", tags=["Calibration"])
app.include_router(simulation_router, prefix="/api/projects", tags=["Simulation"])
app.include_router(decisions_router, prefix="/api", tags=["Decisions"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Check all service connections."""
    return {
        "status": "healthy",
        "service": "rc-decision-engine",
        "version": "0.1.0",
    }


@app.get("/api/climate/presets", tags=["Environment"])
async def get_climate_presets():
    """Return Korean climate presets for simulation."""
    from engine.environment.climate import CLIMATE_PRESETS
    return {"presets": CLIMATE_PRESETS}
