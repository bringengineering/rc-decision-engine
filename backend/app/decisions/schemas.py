"""Decision report request/response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class DecisionRequest(BaseModel):
    climate_preset: Optional[str] = None
    environment_override: Optional[dict[str, Any]] = None
    monte_carlo_n: int = 1000


class DecisionResponse(BaseModel):
    id: UUID
    asset_id: Optional[UUID]
    project_id: UUID
    status: str  # PASS, FAIL, WARNING
    failure_probability: float
    safety_factor_result: float
    safety_factor_target: float
    monte_carlo_n: int
    ucl_95: Optional[float]
    details: dict[str, Any]
    pdf_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
