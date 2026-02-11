"""RabbitMQ consumer — ingests sensor data into InfluxDB.

Runs as a standalone process: `python -m app.sensors.consumer`
Consumes messages from the `sensor.ingest` queue.

Message format (JSON):
{
    "sensor_id": "temp_001",
    "asset_id": "uuid-string",
    "type": "temperature",
    "value": 23.5,
    "timestamp": "2026-02-11T10:00:00Z"  (optional)
}
"""

import asyncio
import json
import logging
from datetime import datetime

import aio_pika

from app.config import settings
from app.db.influxdb import influxdb_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sensor-consumer")

QUEUE_NAME = "sensor.ingest"
EXCHANGE_NAME = "sensor_data"


async def process_message(message: aio_pika.abc.AbstractIncomingMessage):
    """Process a single sensor data message."""
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            timestamp = None
            if "timestamp" in data:
                timestamp = datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))

            influxdb_manager.write_sensor_reading(
                sensor_id=data["sensor_id"],
                asset_id=data.get("asset_id", "unknown"),
                sensor_type=data.get("type", "unknown"),
                value=float(data["value"]),
                timestamp=timestamp,
            )
            logger.debug(f"Ingested: {data['sensor_id']} = {data['value']}")
        except Exception as e:
            logger.error(f"Failed to process message: {e}")


async def main():
    """Start the RabbitMQ consumer."""
    logger.info(f"Connecting to RabbitMQ at {settings.RABBITMQ_URL}")
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=100)

        # Declare exchange and queue
        exchange = await channel.declare_exchange(EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.bind(exchange, routing_key="sensor.#")

        logger.info(f"Listening on queue '{QUEUE_NAME}'...")
        await queue.consume(process_message)

        # Run forever
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
