"""Project Pydantic Schemas"""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


# ─── Road Segment ───

class RoadSegmentCreate(BaseModel):
    segment_id: str
    road_type: str = "straight"
    surface_material: str = "asphalt"
    length_m: float
    width_m: float = 3.5
    lanes: int = 2
    slope_percent: float = 0.0
    elevation_m: float = 0.0
    has_median: bool = False
    has_shoulder: bool = True
    shoulder_width_m: float = 2.0


class RoadSegmentResponse(RoadSegmentCreate):
    id: UUID

    class Config:
        from_attributes = True


# ─── Spray Device ───

class SprayDeviceCreate(BaseModel):
    device_id: str
    position_along_m: float
    position_cross_m: float = 0.0
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    installation_type: str = "flush_mounted"
    burial_depth_mm: float = 0.0
    spray_pattern: str = "fan"
    spray_angle_deg: float = 120.0
    spray_range_m: float = 8.0
    flow_rate_lpm: float = 5.0
    nozzle_diameter_mm: float = 12.0
    brine_concentration_percent: float = 23.0


class SprayDeviceResponse(SprayDeviceCreate):
    id: UUID

    class Config:
        from_attributes = True


# ─── Supply System ───

class SupplySystemCreate(BaseModel):
    tank_capacity_l: float
    pump_pressure_bar: float
    pipe_diameter_mm: float = 50.0
    pipe_material: str = "HDPE"
    pipe_burial_depth_mm: float = 0.0
    has_heating: bool = False
    has_insulation: bool = False


class SupplySystemResponse(SupplySystemCreate):
    id: UUID

    class Config:
        from_attributes = True


# ─── Underground Utility ───

class UndergroundUtilityCreate(BaseModel):
    utility_id: str
    utility_type: str
    depth_mm: float
    position_cross_m: float = 0.0
    diameter_mm: float


class UndergroundUtilityResponse(UndergroundUtilityCreate):
    id: UUID

    class Config:
        from_attributes = True


# ─── Project ───

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    location_name: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime
    road_segments: List[RoadSegmentResponse] = []
    spray_devices: List[SprayDeviceResponse] = []
    supply_system: Optional[SupplySystemResponse] = None
    underground_utilities: List[UndergroundUtilityResponse] = []

    class Config:
        from_attributes = True


class ProjectListItem(BaseModel):
    id: UUID
    name: str
    location_name: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
