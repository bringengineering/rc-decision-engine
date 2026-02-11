"""InfluxDB client wrapper for time-series sensor data."""

from datetime import datetime
from typing import Optional

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

from app.config import settings


class InfluxDBManager:
    """Manages InfluxDB connections for sensor data."""

    def __init__(self):
        self.client = InfluxDBClient(
            url=settings.INFLUXDB_URL,
            token=settings.INFLUXDB_TOKEN,
            org=settings.INFLUXDB_ORG,
        )
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket_raw = settings.INFLUXDB_BUCKET
        self.bucket_historical = "sensor_historical"
        self.org = settings.INFLUXDB_ORG

    def write_sensor_reading(
        self,
        sensor_id: str,
        asset_id: str,
        sensor_type: str,
        value: float,
        timestamp: Optional[datetime] = None,
    ):
        """Write a single sensor reading to the raw bucket."""
        point = (
            Point("sensor_reading")
            .tag("sensor_id", sensor_id)
            .tag("asset_id", asset_id)
            .tag("type", sensor_type)
            .field("value", value)
        )
        if timestamp:
            point = point.time(timestamp, WritePrecision.NS)
        self.write_api.write(bucket=self.bucket_raw, org=self.org, record=point)

    def query_raw(
        self,
        sensor_id: str,
        start: str = "-1h",
        stop: str = "now()",
        aggregation_window: Optional[str] = None,
    ) -> list[dict]:
        """Query raw sensor data."""
        flux = f'''
        from(bucket: "{self.bucket_raw}")
          |> range(start: {start}, stop: {stop})
          |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
          |> filter(fn: (r) => r._measurement == "sensor_reading")
        '''
        if aggregation_window:
            flux += f'  |> aggregateWindow(every: {aggregation_window}, fn: mean, createEmpty: false)\n'
        flux += '  |> sort(columns: ["_time"])'

        tables = self.query_api.query(flux, org=self.org)
        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value(),
                    "sensor_id": record.values.get("sensor_id"),
                    "type": record.values.get("type"),
                })
        return results

    def query_historical(
        self,
        sensor_id: str,
        start: str = "-7d",
        stop: str = "now()",
    ) -> list[dict]:
        """Query downsampled historical data."""
        flux = f'''
        from(bucket: "{self.bucket_historical}")
          |> range(start: {start}, stop: {stop})
          |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
          |> sort(columns: ["_time"])
        '''
        tables = self.query_api.query(flux, org=self.org)
        results = []
        for table in tables:
            for record in table.records:
                results.append({
                    "time": record.get_time().isoformat(),
                    "value": record.get_value(),
                    "measurement": record.get_measurement(),
                })
        return results

    def close(self):
        self.client.close()


influxdb_manager = InfluxDBManager()
