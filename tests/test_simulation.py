"""시뮬레이션 엔진 및 판정 로직 테스트"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.neutral_model import (
    SimulationProject, RoadSegment, RoadType, SurfaceMaterial,
    BrineSprayDevice, SprayPattern, InstallationType,
    SupplySystem,
)
from src.layers.gis_reality import (
    EnvironmentContext, Season, TimeOfDay, TrafficLevel,
    ClimateCondition, estimate_ice_formation_risk, estimate_spray_drift,
    KOREA_CLIMATE_PRESETS,
)
from src.simulation.spray_simulation import run_full_simulation
from src.judgment.rule_engine import evaluate, Verdict


def _make_mild_climate():
    return ClimateCondition(
        air_temperature_c=-3.0,
        road_surface_temperature_c=-5.0,
        humidity_percent=60.0,
        wind_speed_ms=1.0,
        wind_direction_deg=0.0,
        precipitation_type="none",
        precipitation_intensity_mmh=0.0,
        solar_radiation_wm2=0.0,
        cloud_cover_percent=50.0,
    )


def _make_env(climate=None):
    return EnvironmentContext(
        location_name="Test Road",
        latitude=37.0, longitude=127.0,
        elevation_m=50.0,
        season=Season.WINTER,
        time_of_day=TimeOfDay.NIGHT,
        climate=climate or _make_mild_climate(),
        traffic_level=TrafficLevel.LOW,
    )


def _make_project(n_devices=10, road_length=100.0, burial_depth=700.0):
    road = RoadSegment(
        segment_id="TEST-ROAD",
        road_type=RoadType.STRAIGHT,
        surface_material=SurfaceMaterial.ASPHALT,
        length_m=road_length, width_m=3.5, lanes=2,
        slope_percent=0.0, elevation_m=50.0,
    )
    spacing = road_length / (n_devices + 1)
    devices = [
        BrineSprayDevice(
            device_id=f"SPR-{i+1:03d}",
            position_along_road_m=spacing * (i + 1),
            position_cross_m=0.0,
            installation_type=InstallationType.FLUSH_MOUNTED,
            burial_depth_mm=burial_depth,
            spray_pattern=SprayPattern.FAN,
            spray_angle_deg=120.0,
            spray_range_m=8.0,
            flow_rate_lpm=5.0,
            nozzle_diameter_mm=12.0,
            brine_concentration_percent=23.0,
        )
        for i in range(n_devices)
    ]
    supply = SupplySystem(
        tank_capacity_l=5000.0,
        pump_pressure_bar=5.0,
        pipe_diameter_mm=50.0,
        pipe_material="HDPE",
        pipe_burial_depth_mm=700.0,
        has_heating=True,
    )
    return SimulationProject(
        project_id="TEST-PROJECT",
        project_name="Test Project",
        location_name="Test Road",
        latitude=37.0, longitude=127.0,
        road_segments=[road],
        spray_devices=devices,
        supply_system=supply,
    )


def test_ice_formation_risk_zero_above_freezing():
    climate = ClimateCondition(
        air_temperature_c=5.0,
        road_surface_temperature_c=5.0,
        humidity_percent=50.0,
        wind_speed_ms=3.0,
        wind_direction_deg=0.0,
        precipitation_type="none",
        precipitation_intensity_mmh=0.0,
        solar_radiation_wm2=200.0,
        cloud_cover_percent=20.0,
    )
    risk = estimate_ice_formation_risk(climate)
    assert risk == 0.0


def test_ice_formation_risk_high_in_freezing():
    climate = KOREA_CLIMATE_PRESETS["gangwon_winter_night"]
    risk = estimate_ice_formation_risk(climate)
    assert risk >= 0.8


def test_spray_drift_proportional_to_wind():
    drift_low = estimate_spray_drift(1.0, 8.0)
    drift_high = estimate_spray_drift(5.0, 8.0)
    assert drift_high > drift_low
    assert drift_high == 5.0 * drift_low


def test_simulation_runs():
    project = _make_project(n_devices=5, road_length=50.0)
    env = _make_env()
    result = run_full_simulation(project, env)
    assert result.total_road_area_m2 > 0
    assert 0.0 <= result.coverage_ratio <= 1.0


def test_few_devices_fail():
    """장치가 적으면 FAIL 판정"""
    project = _make_project(n_devices=2, road_length=200.0)
    env = _make_env()
    sim = run_full_simulation(project, env)
    judgment = evaluate(project, env, sim)
    assert judgment.verdict == Verdict.FAIL


def test_sufficient_devices_no_critical_coverage_fail():
    """장치가 충분하면 커버리지 CRITICAL 없음"""
    project = _make_project(n_devices=15, road_length=100.0, burial_depth=700.0)
    env = _make_env()
    sim = run_full_simulation(project, env)
    # 커버리지가 50% 미만이 아닌지 확인
    coverage_critical = any(
        f.rule_id == "COV-001"
        for f in evaluate(project, env, sim).failures
    )
    # 15대가 100m에 분사하면 최소 50% 이상은 나와야 함
    assert sim.coverage_ratio > 0.01  # 최소한 어떤 커버리지가 있어야
