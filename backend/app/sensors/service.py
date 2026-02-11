"""Sensor service: InfluxDB queries and sensor mapping management."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SensorMapping
from app.db.influxdb import influxdb_manager


async def create_sensor_mapping(
    db: AsyncSession, asset_id: UUID, sensor_id: str, sensor_type: str, location_description: str | None = None
) -> SensorMapping:
    mapping = SensorMapping(
        asset_id=asset_id,
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        location_description=location_description,
    )
    db.add(mapping)
    await db.flush()
    return mapping


async def get_sensor_mappings(db: AsyncSession, asset_id: UUID) -> list[SensorMapping]:
    result = await db.execute(
        select(SensorMapping).where((SensorMapping.asset_id == asset_id) & (SensorMapping.is_active.is_(True)))
    )
    return list(result.scalars().all())


def query_sensor_data(sensor_id: str, start: str = "-1h", stop: str = "now()", aggregation_window: str | None = None) -> list[dict]:
    """Query raw sensor data from InfluxDB."""
    return influxdb_manager.query_raw(sensor_id, start=start, stop=stop, aggregation_window=aggregation_window)


def query_historical_data(sensor_id: str, start: str = "-7d", stop: str = "now()") -> list[dict]:
    """Query downsampled historical data from InfluxDB."""
    return influxdb_manager.query_historical(sensor_id, start=start, stop=stop)
