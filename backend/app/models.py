"""
SQLAlchemy ORM Models
All database tables defined here
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, Text,
    ForeignKey, DateTime, JSON, Enum as SAEnum,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography

from app.database import Base


# ─── Users & Organizations ───

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    plan = Column(String(20), default="starter")  # starter, professional, team, enterprise
    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="organization")
    projects = relationship("Project", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)  # null for OAuth users
    provider = Column(String(50), default="local")  # local, kakao, google
    provider_id = Column(String(255), nullable=True)  # OAuth provider user ID
    role = Column(String(20), default="engineer")  # admin, engineer, viewer
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="users")
    projects = relationship("Project", back_populates="owner")


# ─── Projects ───

class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location_name = Column(String(200), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(String(20), default="draft")  # draft, simulating, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    organization = relationship("Organization", back_populates="projects")
    road_segments = relationship("RoadSegment", back_populates="project", cascade="all, delete-orphan")
    spray_devices = relationship("SprayDevice", back_populates="project", cascade="all, delete-orphan")
    supply_system = relationship("SupplySystem", back_populates="project", uselist=False, cascade="all, delete-orphan")
    underground_utilities = relationship("UndergroundUtility", back_populates="project", cascade="all, delete-orphan")
    simulation_runs = relationship("SimulationRun", back_populates="project", cascade="all, delete-orphan")


# ─── Road Segments ───

class RoadSegment(Base):
    __tablename__ = "road_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(String(50), nullable=False)
    road_type = Column(String(30), nullable=False)  # straight, curve, bridge, etc.
    surface_material = Column(String(30), nullable=False)  # asphalt, concrete, steel_deck
    length_m = Column(Float, nullable=False)
    width_m = Column(Float, nullable=False)
    lanes = Column(Integer, nullable=False)
    slope_percent = Column(Float, default=0.0)
    elevation_m = Column(Float, default=0.0)
    has_median = Column(Boolean, default=False)
    has_shoulder = Column(Boolean, default=True)
    shoulder_width_m = Column(Float, default=2.0)
    properties = Column(JSONB, default={})

    project = relationship("Project", back_populates="road_segments")


# ─── Spray Devices ───

class SprayDevice(Base):
    __tablename__ = "spray_devices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    device_id = Column(String(50), nullable=False)
    position_along_m = Column(Float, nullable=False)
    position_cross_m = Column(Float, default=0.0)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    installation_type = Column(String(30), nullable=False)  # surface_mounted, flush_mounted, buried
    burial_depth_mm = Column(Float, default=0.0)
    spray_pattern = Column(String(20), nullable=False)  # linear, fan, full_circle
    spray_angle_deg = Column(Float, nullable=False)
    spray_range_m = Column(Float, nullable=False)
    flow_rate_lpm = Column(Float, nullable=False)
    nozzle_diameter_mm = Column(Float, default=12.0)
    brine_concentration_percent = Column(Float, default=23.0)
    properties = Column(JSONB, default={})

    project = relationship("Project", back_populates="spray_devices")


# ─── Supply System ───

class SupplySystem(Base):
    __tablename__ = "supply_systems"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, unique=True)
    tank_capacity_l = Column(Float, nullable=False)
    pump_pressure_bar = Column(Float, nullable=False)
    pipe_diameter_mm = Column(Float, nullable=False)
    pipe_material = Column(String(50), default="HDPE")
    pipe_burial_depth_mm = Column(Float, default=0.0)
    has_heating = Column(Boolean, default=False)
    has_insulation = Column(Boolean, default=False)

    project = relationship("Project", back_populates="supply_system")


# ─── Underground Utilities ───

class UndergroundUtility(Base):
    __tablename__ = "underground_utilities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    utility_id = Column(String(50), nullable=False)
    utility_type = Column(String(30), nullable=False)  # gas, water, electric, telecom, sewer
    depth_mm = Column(Float, nullable=False)
    position_cross_m = Column(Float, default=0.0)
    diameter_mm = Column(Float, nullable=False)

    project = relationship("Project", back_populates="underground_utilities")


# ─── Simulation Runs ───

class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    triggered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    climate_preset = Column(String(50), nullable=True)
    climate_data = Column(JSONB, nullable=False)
    status = Column(String(20), default="queued")  # queued, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    result = Column(JSONB, nullable=True)  # SimulationResult
    judgment = Column(JSONB, nullable=True)  # JudgmentResult (verdict, failures, etc.)
    report_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="simulation_runs")
    user = relationship("User")
