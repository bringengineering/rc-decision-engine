"""Sensor API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.sensors.schemas import (
    SensorMappingCreate, SensorMappingResponse, SensorDataQuery, SensorDataPoint,
)
from app.sensors import service

router = APIRouter()


@router.get("/{sensor_id}/data", response_model=list[SensorDataPoint])
async def get_sensor_data(
    sensor_id: str,
    start: str = "-1h",
    stop: str = "now()",
    aggregation_window: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Query raw sensor data from InfluxDB."""
    return service.query_sensor_data(sensor_id, start=start, stop=stop, aggregation_window=aggregation_window)


@router.get("/{sensor_id}/historical", response_model=list[SensorDataPoint])
async def get_historical_data(
    sensor_id: str,
    start: str = "-7d",
    stop: str = "now()",
    current_user: User = Depends(get_current_user),
):
    """Query downsampled historical data from InfluxDB."""
    return service.query_historical_data(sensor_id, start=start, stop=stop)


@router.get("/asset/{asset_id}/mappings", response_model=list[SensorMappingResponse])
async def get_asset_sensors(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List sensors mapped to an asset."""
    return await service.get_sensor_mappings(db, asset_id)


@router.post("/asset/{asset_id}/mappings", response_model=SensorMappingResponse, status_code=201)
async def create_sensor_mapping(
    asset_id: UUID,
    data: SensorMappingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Map a sensor to an asset."""
    return await service.create_sensor_mapping(
        db, asset_id, data.sensor_id, data.sensor_type, data.location_description
    )


@router.get("/health")
async def sensor_health(current_user: User = Depends(get_current_user)):
    """Check InfluxDB connectivity."""
    try:
        from app.db.influxdb import influxdb_manager
        health = influxdb_manager.client.health()
        return {"status": health.status, "message": health.message}
    except Exception as e:
        return {"status": "error", "message": str(e)}
