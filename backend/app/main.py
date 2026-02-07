"""
Brine Spray Simulation Engine — FastAPI Application
Main entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.auth.router import router as auth_router
from app.projects.router import router as projects_router
from app.simulation.router import router as simulation_router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Problem-Driven BIM Simulation Engine for road ice prevention brine spray systems.",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(simulation_router)


@app.get("/api/health")
async def health_check():
    from app.database import check_db_connection
    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/api/climate/presets")
async def list_climate_presets():
    """사용 가능한 기후 프리셋 목록"""
    from engine.gis_reality import KOREA_CLIMATE_PRESETS
    from dataclasses import asdict
    return {
        key: asdict(climate)
        for key, climate in KOREA_CLIMATE_PRESETS.items()
    }


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs",
        "message": "Engineering ideas must survive reality, not explanations.",
    }
