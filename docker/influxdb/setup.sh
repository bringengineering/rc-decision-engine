#!/bin/bash
# Create the historical bucket with infinite retention
influx bucket create \
  --name sensor_historical \
  --org "${DOCKER_INFLUXDB_INIT_ORG}" \
  --retention 0 \
  --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" 2>/dev/null || true

# Create downsampling task: 10-minute aggregation
influx task create \
  --org "${DOCKER_INFLUXDB_INIT_ORG}" \
  --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
  --flux '
option task = {name: "downsample_10m", every: 10m}

from(bucket: "sensor_raw")
  |> range(start: -20m)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> aggregateWindow(every: 10m, fn: mean, createEmpty: false)
  |> set(key: "_measurement", value: "sensor_reading_mean")
  |> to(bucket: "sensor_historical", org: "rcengine")
' 2>/dev/null || true

influx task create \
  --org "${DOCKER_INFLUXDB_INIT_ORG}" \
  --token "${DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}" \
  --flux '
option task = {name: "downsample_10m_max", every: 10m}

from(bucket: "sensor_raw")
  |> range(start: -20m)
  |> filter(fn: (r) => r._measurement == "sensor_reading")
  |> aggregateWindow(every: 10m, fn: max, createEmpty: false)
  |> set(key: "_measurement", value: "sensor_reading_max")
  |> to(bucket: "sensor_historical", org: "rcengine")
' 2>/dev/null || true

echo "InfluxDB setup complete: sensor_historical bucket + downsampling tasks created"
