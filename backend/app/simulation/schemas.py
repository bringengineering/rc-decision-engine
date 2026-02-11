"""Simulation request/response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class SimulationRequest(BaseModel):
    simulation_type: str = "salt_spray"  # salt_spray, thermal, structural, fluid
    climate_preset: Optional[str] = None  # e.g. "gangwon_winter_severe"
    environment_override: Optional[dict[str, Any]] = None
    monte_carlo_n: int = 1000
    params_override: Optional[dict[str, Any]] = None


class SimulationStatusResponse(BaseModel):
    run_id: UUID
    status: str  # queued, running, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class SimulationResultResponse(BaseModel):
    run_id: UUID
    status: str
    simulation_type: str
    result: Optional[dict[str, Any]] = None
    decision: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}
