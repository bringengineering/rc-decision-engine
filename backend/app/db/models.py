"""SQLAlchemy ORM models for PostgreSQL."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)
    provider = Column(String(50), default="local")  # local, kakao, google
    provider_id = Column(String(255), nullable=True)
    role = Column(String(20), default="engineer")  # admin, engineer, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    projects = relationship("Project", back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    safety_factor_target = Column(Float, default=1.5)
    location_code = Column(String(50), nullable=True)  # KDS region code
    location_name = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), default="draft")  # draft, active, archived
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="projects")
    assets = relationship("Asset", back_populates="project", cascade="all, delete-orphan")
    simulation_runs = relationship("SimulationRun", back_populates="project", cascade="all, delete-orphan")
    decision_reports = relationship("DecisionReport", back_populates="project", cascade="all, delete-orphan")


class Asset(Base):
    """Unified asset model — replaces separate road/device/utility tables.

    The `type` field determines what schema `properties` JSONB follows.
    The `bim_element_id` maps to a Revit GUID for future plugin integration.
    """
    __tablename__ = "assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    bim_element_id = Column(String(255), nullable=True)  # Revit GUID
    type = Column(String(50), nullable=False)  # road_segment, spray_device, supply_system, bridge_pier, jet_fan, curb
    name = Column(String(200), nullable=True)
    geometry_json = Column(JSONB, nullable=True)  # Simplified geometry (convex hull, line, point)
    properties = Column(JSONB, nullable=True)  # Type-specific properties
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    project = relationship("Project", back_populates="assets")
    calibration_state = relationship("CalibrationState", back_populates="asset", uselist=False, cascade="all, delete-orphan")
    decision_reports = relationship("DecisionReport", back_populates="asset", cascade="all, delete-orphan")
    sensor_mappings = relationship("SensorMapping", back_populates="asset", cascade="all, delete-orphan")


class CalibrationState(Base):
    """Tracks the reality-calibration state per asset.

    physics_params stores the current calibrated boundary conditions.
    When drift > 5% for > 10 minutes, re-calibration is triggered.
    """
    __tablename__ = "calibration_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False)
    physics_params = Column(JSONB, default=dict)  # e.g. {"friction": 0.4, "drag_coeff": 1.2}
    drift_history = Column(JSONB, default=list)  # Recent drift measurements
    last_calibrated_at = Column(DateTime, nullable=True)
    calibration_count = Column(Integer, default=0)
    status = Column(String(20), default="uncalibrated")  # uncalibrated, calibrated, drifting, recalibrating

    asset = relationship("Asset", back_populates="calibration_state")


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    simulation_type = Column(String(50), nullable=False)  # salt_spray, thermal, structural, fluid
    input_params = Column(JSONB, default=dict)
    climate_data = Column(JSONB, default=dict)
    status = Column(String(20), default="queued")  # queued, running, completed, failed
    result = Column(JSONB, nullable=True)
    mesh_file_url = Column(String(500), nullable=True)  # MinIO URL
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="simulation_runs")
    decision_reports = relationship("DecisionReport", back_populates="simulation_run")


class DecisionReport(Base):
    """Stores PASS/FAIL/WARNING decisions from The Judge.

    Each report corresponds to a Monte Carlo analysis of an asset
    under specific environmental conditions.
    """
    __tablename__ = "decision_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    simulation_run_id = Column(UUID(as_uuid=True), ForeignKey("simulation_runs.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), nullable=False)  # PASS, FAIL, WARNING
    failure_probability = Column(Float, nullable=False)  # Pf from Monte Carlo
    safety_factor_result = Column(Float, nullable=False)  # Computed mean SF
    safety_factor_target = Column(Float, nullable=False)  # Target SF from project
    monte_carlo_n = Column(Integer, default=1000)
    ucl_95 = Column(Float, nullable=True)  # 95% Upper Confidence Limit
    details = Column(JSONB, default=dict)  # Full breakdown
    pdf_url = Column(String(500), nullable=True)  # MinIO URL to PDF report
    created_at = Column(DateTime, server_default=func.now())

    asset = relationship("Asset", back_populates="decision_reports")
    project = relationship("Project", back_populates="decision_reports")
    simulation_run = relationship("SimulationRun", back_populates="decision_reports")


class SensorMapping(Base):
    """Links InfluxDB sensor IDs to PostgreSQL assets."""
    __tablename__ = "sensor_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    sensor_id = Column(String(100), nullable=False)  # Matches InfluxDB tag
    sensor_type = Column(String(50), nullable=False)  # temperature, humidity, wind_speed, strain
    location_description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    asset = relationship("Asset", back_populates="sensor_mappings")
