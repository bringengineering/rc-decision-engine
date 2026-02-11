"""Sensor data request/response schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SensorMappingCreate(BaseModel):
    sensor_id: str
    sensor_type: str  # temperature, humidity, wind_speed, strain
    location_description: Optional[str] = None


class SensorMappingResponse(BaseModel):
    id: UUID
    asset_id: UUID
    sensor_id: str
    sensor_type: str
    location_description: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SensorDataQuery(BaseModel):
    start: str = "-1h"
    stop: str = "now()"
    aggregation_window: Optional[str] = None


class SensorDataPoint(BaseModel):
    time: str
    value: float
    sensor_id: Optional[str] = None
    type: Optional[str] = None
