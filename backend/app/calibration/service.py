"""Calibration service: manages asset calibration state."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CalibrationState, Asset


async def get_calibration_state(db: AsyncSession, asset_id: UUID) -> CalibrationState | None:
    result = await db.execute(
        select(CalibrationState).where(CalibrationState.asset_id == asset_id)
    )
    return result.scalar_one_or_none()


async def create_or_update_calibration(
    db: AsyncSession,
    asset_id: UUID,
    physics_params: dict,
    drift_pct: float = 0.0,
    status: str = "calibrated",
) -> CalibrationState:
    state = await get_calibration_state(db, asset_id)
    if state is None:
        state = CalibrationState(
            asset_id=asset_id,
            physics_params=physics_params,
            drift_history=[{"drift_pct": drift_pct, "at": datetime.now(timezone.utc).isoformat()}],
            last_calibrated_at=datetime.now(timezone.utc),
            calibration_count=1,
            status=status,
        )
        db.add(state)
    else:
        state.physics_params = physics_params
        history = state.drift_history or []
        history.append({"drift_pct": drift_pct, "at": datetime.now(timezone.utc).isoformat()})
        # Keep last 100 entries
        state.drift_history = history[-100:]
        state.last_calibrated_at = datetime.now(timezone.utc)
        state.calibration_count = (state.calibration_count or 0) + 1
        state.status = status

    await db.flush()
    return state


async def trigger_calibration(db: AsyncSession, asset_id: UUID) -> dict:
    """Trigger a calibration cycle for an asset.

    In Phase 1 MVP, this does a simple parameter adjustment.
    In Phase 2+, this will invoke PINNs fine-tuning.
    """
    from engine.calibration.drift_detector import DriftDetector
    from engine.calibration.calibrator import Calibrator

    detector = DriftDetector()
    calibrator = Calibrator()

    # Get current state
    state = await get_calibration_state(db, asset_id)
    current_params = state.physics_params if state else {}

    # Detect drift (placeholder - would use InfluxDB data in production)
    drift_pct = detector.compute_drift(current_params, sensor_data={})

    if drift_pct > 5.0:
        result = calibrator.calibrate(current_params, sensor_data={})
        await create_or_update_calibration(
            db, asset_id, result.new_physics_params, drift_pct=drift_pct, status="calibrated"
        )
        return {
            "status": "recalibrated",
            "message": f"Drift {drift_pct:.1f}% detected, parameters recalibrated",
            "drift_percentage": drift_pct,
            "corrections": result.corrections_applied,
        }
    else:
        return {
            "status": "ok",
            "message": f"Drift {drift_pct:.1f}% is within threshold (5%)",
            "drift_percentage": drift_pct,
            "corrections": None,
        }
