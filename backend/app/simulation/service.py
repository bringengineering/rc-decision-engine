"""Simulation Service — bridges DB models to engine"""

from dataclasses import asdict
from typing import Tuple

from app.models import Project

# Import the simulation engine (migrated from prototype)
import sys
import os
engine_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "engine")
if engine_path not in sys.path:
    sys.path.insert(0, os.path.dirname(engine_path))

from engine.neutral_model import (
    SimulationProject as EngineProject,
    RoadSegment as EngineRoad,
    RoadType, SurfaceMaterial,
    BrineSprayDevice as EngineDevice,
    SprayPattern, InstallationType,
    SupplySystem as EngineSupply,
    UndergroundUtility as EngineUtility,
)
from engine.gis_reality import (
    EnvironmentContext, Season, TimeOfDay, TrafficLevel,
    KOREA_CLIMATE_PRESETS, estimate_ice_formation_risk,
)
from engine.spray_simulation import run_full_simulation
from engine.rule_engine import evaluate
from engine.report_generator import generate_report


def build_engine_project(project: Project) -> EngineProject:
    """DB Project model → Engine SimulationProject"""

    roads = []
    for r in project.road_segments:
        roads.append(EngineRoad(
            segment_id=r.segment_id,
            road_type=RoadType(r.road_type),
            surface_material=SurfaceMaterial(r.surface_material),
            length_m=r.length_m,
            width_m=r.width_m,
            lanes=r.lanes,
            slope_percent=r.slope_percent or 0.0,
            elevation_m=r.elevation_m or 0.0,
            has_median=r.has_median or False,
            has_shoulder=r.has_shoulder if r.has_shoulder is not None else True,
            shoulder_width_m=r.shoulder_width_m or 2.0,
        ))

    devices = []
    for d in project.spray_devices:
        devices.append(EngineDevice(
            device_id=d.device_id,
            position_along_road_m=d.position_along_m,
            position_cross_m=d.position_cross_m or 0.0,
            installation_type=InstallationType(d.installation_type),
            burial_depth_mm=d.burial_depth_mm or 0.0,
            spray_pattern=SprayPattern(d.spray_pattern),
            spray_angle_deg=d.spray_angle_deg,
            spray_range_m=d.spray_range_m,
            flow_rate_lpm=d.flow_rate_lpm,
            nozzle_diameter_mm=d.nozzle_diameter_mm or 12.0,
            brine_concentration_percent=d.brine_concentration_percent or 23.0,
        ))

    supply = None
    if project.supply_system:
        s = project.supply_system
        supply = EngineSupply(
            tank_capacity_l=s.tank_capacity_l,
            pump_pressure_bar=s.pump_pressure_bar,
            pipe_diameter_mm=s.pipe_diameter_mm,
            pipe_material=s.pipe_material or "HDPE",
            pipe_burial_depth_mm=s.pipe_burial_depth_mm or 0.0,
            has_heating=s.has_heating or False,
            has_insulation=s.has_insulation or False,
        )

    utilities = []
    for u in project.underground_utilities:
        utilities.append(EngineUtility(
            utility_id=u.utility_id,
            utility_type=u.utility_type,
            depth_mm=u.depth_mm,
            position_cross_m=u.position_cross_m or 0.0,
            diameter_mm=u.diameter_mm,
        ))

    return EngineProject(
        project_id=str(project.id),
        project_name=project.name,
        location_name=project.location_name or "",
        latitude=project.latitude or 0.0,
        longitude=project.longitude or 0.0,
        road_segments=roads,
        spray_devices=devices,
        supply_system=supply,
        underground_utilities=utilities,
    )


def build_environment(project: Project, climate_preset: str) -> EnvironmentContext:
    """Build environment context from project + climate preset"""

    if climate_preset not in KOREA_CLIMATE_PRESETS:
        climate_preset = "gangwon_winter_night"

    climate = KOREA_CLIMATE_PRESETS[climate_preset]

    elevation = 0.0
    if project.road_segments:
        elevation = project.road_segments[0].elevation_m or 0.0

    return EnvironmentContext(
        location_name=project.location_name or "Unknown",
        latitude=project.latitude or 0.0,
        longitude=project.longitude or 0.0,
        elevation_m=elevation,
        season=Season.WINTER,
        time_of_day=TimeOfDay.NIGHT,
        climate=climate,
        traffic_level=TrafficLevel.LOW,
    )


def run_simulation_sync(engine_project: EngineProject, env: EnvironmentContext) -> Tuple[dict, dict, str]:
    """
    Run full simulation pipeline and return serializable results.
    Returns: (sim_result_dict, judgment_dict, report_text)
    """
    # 1. Run simulation
    sim_result = run_full_simulation(engine_project, env, resolution_m=1.0)

    # 2. Evaluate (Failure-First)
    judgment = evaluate(engine_project, env, sim_result)

    # 3. Generate report
    report_text = generate_report(engine_project, env, sim_result, judgment)

    # 4. Serialize to dicts (for JSON storage)
    sim_dict = {
        "total_road_area_m2": sim_result.total_road_area_m2,
        "covered_area_m2": sim_result.covered_area_m2,
        "coverage_ratio": sim_result.coverage_ratio,
        "uncovered_zones": sim_result.uncovered_zones,
        "overlap_area_m2": sim_result.overlap_area_m2,
        "total_brine_consumption_lph": sim_result.total_brine_consumption_lph,
        "device_results": [
            {
                "device_id": dr.device_id,
                "effective_range_m": dr.effective_range_m,
                "drift_offset_m": dr.drift_offset_m,
                "coverage_area_m2": dr.coverage_area_m2,
                "brine_consumption_lpm": dr.brine_consumption_lpm,
            }
            for dr in sim_result.device_results
        ],
    }

    judgment_dict = {
        "verdict": judgment.verdict.value,
        "confidence": judgment.confidence,
        "summary": judgment.summary,
        "failures": [
            {
                "rule_id": f.rule_id,
                "category": f.category,
                "severity": f.severity.value,
                "description": f.description,
                "evidence": f.evidence,
                "recommendation": f.recommendation,
            }
            for f in judgment.failures
        ],
        "conditions": judgment.conditions,
        "limitations": judgment.limitations,
    }

    return sim_dict, judgment_dict, report_text
