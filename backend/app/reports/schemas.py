"""Report request/response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ReportGenerateRequest(BaseModel):
    decision_id: Optional[UUID] = None  # Generate from specific decision
    include_all_assets: bool = True


class ReportResponse(BaseModel):
    id: UUID
    project_id: UUID
    status: str
    pdf_url: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
