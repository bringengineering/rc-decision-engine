"""Calibration API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.calibration.schemas import CalibrationStateResponse, CalibrationTriggerResponse, DriftResponse
from app.calibration import service

router = APIRouter()


@router.get("/{asset_id}/calibration", response_model=CalibrationStateResponse)
async def get_calibration(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current calibration state for an asset."""
    state = await service.get_calibration_state(db, asset_id)
    if not state:
        raise HTTPException(status_code=404, detail="No calibration state found")
    return state


@router.post("/{asset_id}/calibration/trigger", response_model=CalibrationTriggerResponse)
async def trigger_calibration(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger re-calibration for an asset."""
    result = await service.trigger_calibration(db, asset_id)
    return CalibrationTriggerResponse(**result)


@router.get("/{asset_id}/calibration/drift", response_model=DriftResponse)
async def get_drift(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get drift history and current drift percentage."""
    state = await service.get_calibration_state(db, asset_id)
    history = state.drift_history if state else []
    current_drift = history[-1]["drift_pct"] if history else 0.0
    return DriftResponse(
        asset_id=asset_id,
        current_drift_pct=current_drift,
        is_drifting=current_drift > 5.0,
        history=history[-20:],
    )
