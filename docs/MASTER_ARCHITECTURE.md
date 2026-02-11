# Master Architecture: Reality-Calibrated Decision Support System

> "CAD is for drawing; We are for deciding."

## System Identity
This system substitutes the TRL 1-3 decision-making process for civil engineering infrastructure.
It combines Physics Engines (Ideal) with Sensor Data (Real) to provide calibrated PASS/FAIL decisions.

## Architecture Overview
- **Frontend:** Autodesk Revit Plugin (C# / .NET 8) — Phase 2+
- **Backend:** Python FastAPI — PINNs, Physics, Calibration, REST API
- **Message Queue:** RabbitMQ — sensor data buffering
- **Database:** PostgreSQL + InfluxDB + MinIO

## Core Algorithms
1. **PINNs:** L_total = L_physics + lambda * L_sensor
2. **Monte Carlo:** N=1000, PASS/FAIL/WARNING
3. **Calibration:** Drift > 5% for > 10min triggers re-calibration
4. **Imputation:** Physics-based (not simple average)

## Decision Rules
- FAIL: Pf >= 20% OR SF < 1.0
- WARNING: Mean safe but UCL95% violates
- PASS: SF >= 1.5

## Development Phases
- Phase 1: Salt Spray MVP
- Phase 2: Tunnels/Bridges
- Phase 3: GPU Acceleration
