"""Calibration request/response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class CalibrationStateResponse(BaseModel):
    id: UUID
    asset_id: UUID
    physics_params: dict[str, Any]
    drift_history: list
    last_calibrated_at: Optional[datetime]
    calibration_count: int
    status: str

    model_config = {"from_attributes": True}


class CalibrationTriggerResponse(BaseModel):
    status: str
    message: str
    drift_percentage: Optional[float] = None
    corrections: Optional[dict[str, float]] = None


class DriftResponse(BaseModel):
    asset_id: UUID
    current_drift_pct: float
    is_drifting: bool
    history: list
