"""Setup InfluxDB buckets and downsampling tasks."""

from influxdb_client import InfluxDBClient, BucketRetentionRules
from app.config import settings


def setup():
    client = InfluxDBClient(
        url=settings.INFLUXDB_URL,
        token=settings.INFLUXDB_TOKEN,
        org=settings.INFLUXDB_ORG,
    )
    buckets_api = client.buckets_api()

    # Create sensor_historical bucket (infinite retention)
    try:
        buckets_api.create_bucket(
            bucket_name="sensor_historical",
            retention_rules=[BucketRetentionRules(type="expire", every_seconds=0)],
            org=settings.INFLUXDB_ORG,
        )
        print("Created bucket: sensor_historical (infinite retention)")
    except Exception as e:
        print(f"Bucket may already exist: {e}")

    client.close()
    print("InfluxDB setup complete")


if __name__ == "__main__":
    setup()
