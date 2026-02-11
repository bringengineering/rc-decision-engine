"""Pydantic domain models for the computation engine.

These models are independent of SQLAlchemy — they represent
the computational domain, not the database schema.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field

from engine.domain.enums import AssetType, Verdict, SimulationType
from engine.domain.constants import KDS_MIN_SAFETY_FACTOR, MONTE_CARLO_N


# ===== Geometry Models =====

class Point3D(BaseModel):
    x: float
    y: float
    z: float = 0.0


class LineSegment(BaseModel):
    start: Point3D
    end: Point3D

    @property
    def length(self) -> float:
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        dz = self.end.z - self.start.z
        return (dx**2 + dy**2 + dz**2) ** 0.5


# ===== Environment Models =====

class EnvironmentCondition(BaseModel):
    temperature: float = 0.0  # °C
    humidity: float = 70.0  # %
    wind_speed: float = 3.0  # m/s
    wind_direction: float = 0.0  # degrees from North
    precipitation: float = 0.0  # mm/hr
    solar_radiation: float = 0.0  # W/m^2
    road_surface_temp: Optional[float] = None  # °C (if measured)


class ClimatePreset(BaseModel):
    name: str
    region: str
    conditions: EnvironmentCondition


# ===== Asset Models =====

class PhysicsAsset(BaseModel):
    """Base asset model for physics computation."""
    id: str
    type: AssetType
    name: Optional[str] = None
    geometry: Optional[dict[str, Any]] = None
    properties: dict[str, Any] = Field(default_factory=dict)


class SprayDeviceParams(BaseModel):
    """Parameters specific to a spray device."""
    nozzle_diameter: float = 0.003  # m
    spray_angle: float = 60.0  # degrees
    flow_rate: float = 0.5  # L/min
    pump_pressure: float = 300000.0  # Pa
    brine_concentration: float = 23.0  # %
    mounting_height: float = 0.3  # m
    orientation: float = 0.0  # degrees


class RoadSegmentParams(BaseModel):
    """Parameters specific to a road segment."""
    length: float  # m
    width: float  # m
    lanes: int = 2
    slope: float = 0.0  # %
    surface_material: str = "asphalt"
    elevation: float = 0.0  # m


# ===== Simulation I/O =====

class SimulationInput(BaseModel):
    """Input to the simulation engine."""
    project_id: str
    simulation_type: SimulationType
    assets: list[PhysicsAsset]
    environment: EnvironmentCondition
    safety_factor_target: float = KDS_MIN_SAFETY_FACTOR
    monte_carlo_n: int = MONTE_CARLO_N
    calibration_params: Optional[dict[str, Any]] = None


class CoverageResult(BaseModel):
    """Result from spray coverage calculation."""
    coverage_ratio: float  # 0.0 to 1.0
    coverage_area: float  # m^2
    total_area: float  # m^2
    spray_pattern: Optional[dict[str, Any]] = None  # Detailed spray field


class SimulationOutput(BaseModel):
    """Output from the simulation engine."""
    simulation_type: SimulationType
    coverage: Optional[CoverageResult] = None
    temperature_field: Optional[dict[str, Any]] = None
    flow_field: Optional[dict[str, Any]] = None
    safety_factors: list[float] = Field(default_factory=list)
    mean_safety_factor: float = 0.0
    raw_results: Optional[dict[str, Any]] = None


# ===== Decision Models =====

class DecisionResult(BaseModel):
    """The Judge's final decision."""
    verdict: Verdict
    failure_probability: float  # Pf
    mean_safety_factor: float
    safety_factor_target: float
    ucl_95: Optional[float] = None
    monte_carlo_n: int = MONTE_CARLO_N
    details: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""  # Human-readable explanation


class CalibrationResult(BaseModel):
    """Result from a calibration cycle."""
    drift_percentage: float
    corrections_applied: dict[str, float]  # param_name -> correction_value
    new_physics_params: dict[str, Any]
    sensor_readings_used: int
    status: str  # "calibrated", "insufficient_data"
