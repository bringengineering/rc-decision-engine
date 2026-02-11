"""Asset request/response schemas."""

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class AssetCreate(BaseModel):
    bim_element_id: Optional[str] = None
    type: str  # road_segment, spray_device, supply_system, bridge_pier, jet_fan, curb
    name: Optional[str] = None
    geometry_json: Optional[dict[str, Any]] = None
    properties: Optional[dict[str, Any]] = None


class AssetUpdate(BaseModel):
    bim_element_id: Optional[str] = None
    name: Optional[str] = None
    geometry_json: Optional[dict[str, Any]] = None
    properties: Optional[dict[str, Any]] = None


class AssetResponse(BaseModel):
    id: UUID
    project_id: UUID
    bim_element_id: Optional[str]
    type: str
    name: Optional[str]
    geometry_json: Optional[dict[str, Any]]
    properties: Optional[dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AssetBulkCreate(BaseModel):
    """Bulk import from Revit — array of assets."""
    assets: list[AssetCreate]
