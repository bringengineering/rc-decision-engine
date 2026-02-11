# RC Decision Engine

**Reality-Calibrated Decision Support System**

> "CAD is for drawing; We are for deciding."

A pre-installation design validation platform that substitutes the TRL 1-3 decision-making process for civil engineering infrastructure. Combines Physics Engines (Ideal) with Sensor Data (Real) to provide calibrated PASS/FAIL decisions.

## Architecture

```
Revit Plugin (C#) ──> FastAPI Backend (Python) ──> PostgreSQL (Metadata)
                           │
                 ┌─────────┼─────────┐
                 ▼         ▼         ▼
           InfluxDB    MinIO     Redis
           (Sensor)    (S3)     (Cache)
                 ▲
                 │
            RabbitMQ
            (Queue)
```

## Core Capabilities

- **PINNs Engine**: Physics-Informed Neural Networks calibrated with real sensor data
- **Monte Carlo Decision**: N=1000 simulations -> PASS / WARNING / FAIL classification
- **Reality Calibration**: Auto-corrects physics drift when sensor error > 5% for > 10min
- **Legal Reports**: PDF with KDS verification, calibration records, TRL 1-3 due diligence

## Quick Start

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start all services
docker-compose up -d

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Open API docs
open http://localhost:8000/api/docs
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Backend (FastAPI) | 8000 | REST API + WebSocket |
| PostgreSQL | 5432 | Relational metadata |
| InfluxDB | 8086 | Time-series sensor data |
| RabbitMQ | 5672 / 15672 | Message queue / Management UI |
| MinIO | 9000 / 9001 | Object storage / Console |
| Redis | 6379 | Cache + Celery broker |

## Development Roadmap

- **Phase 1 (MVP)**: Salt Spray System - Road Curbs & Icing
- **Phase 2**: Tunnels & Bridges - Jet Fans & Bridge Piers
- **Phase 3**: Real-time optimization with GPU acceleration

## License

MIT
