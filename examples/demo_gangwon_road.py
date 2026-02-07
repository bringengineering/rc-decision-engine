"""
데모 시나리오: 강원도 산간 도로 염수분사장치 배치 시뮬레이션

시나리오:
- 강원도 산간 지역 200m 도로 구간
- 2차선 도로, 경사 3%
- 겨울 야간, 폭설 조건
- 염수분사장치 3대 배치
- 가스관 지하 매설물 존재

이 시나리오는 의도적으로 몇 가지 문제를 포함하고 있습니다:
1. 장치 간격이 넓어 미커버 구간 발생
2. 매립 깊이가 동결심도보다 얕음
3. 가스관과의 이격 거리 부족
"""

import sys
import os

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.neutral_model import (
    SimulationProject, RoadSegment, RoadType, SurfaceMaterial,
    BrineSprayDevice, SprayPattern, InstallationType,
    SupplySystem, UndergroundUtility,
)
from src.layers.gis_reality import (
    EnvironmentContext, Season, TimeOfDay, TrafficLevel,
    KOREA_CLIMATE_PRESETS, estimate_ice_formation_risk,
)
from src.simulation.spray_simulation import run_full_simulation
from src.judgment.rule_engine import evaluate
from src.report.report_generator import generate_report


def create_project() -> SimulationProject:
    """데모 프로젝트 생성"""

    road = RoadSegment(
        segment_id="GW-ROAD-001",
        road_type=RoadType.CURVE,
        surface_material=SurfaceMaterial.ASPHALT,
        length_m=200.0,
        width_m=3.5,
        lanes=2,
        slope_percent=3.0,
        elevation_m=450.0,
        has_median=False,
        has_shoulder=True,
        shoulder_width_m=1.5,
    )

    # 장치 3대: 의도적으로 간격을 넓게 배치 (문제 유발)
    devices = [
        BrineSprayDevice(
            device_id="SPR-001",
            position_along_road_m=20.0,
            position_cross_m=0.0,
            installation_type=InstallationType.FLUSH_MOUNTED,
            burial_depth_mm=400.0,  # 동결심도(900mm)보다 얕음!
            spray_pattern=SprayPattern.FAN,
            spray_angle_deg=120.0,
            spray_range_m=8.0,
            flow_rate_lpm=5.0,
            nozzle_diameter_mm=12.0,
            brine_concentration_percent=23.0,
        ),
        BrineSprayDevice(
            device_id="SPR-002",
            position_along_road_m=100.0,
            position_cross_m=0.0,
            installation_type=InstallationType.FLUSH_MOUNTED,
            burial_depth_mm=400.0,
            spray_pattern=SprayPattern.FAN,
            spray_angle_deg=120.0,
            spray_range_m=8.0,
            flow_rate_lpm=5.0,
            nozzle_diameter_mm=12.0,
            brine_concentration_percent=23.0,
        ),
        BrineSprayDevice(
            device_id="SPR-003",
            position_along_road_m=180.0,
            position_cross_m=0.0,
            installation_type=InstallationType.FLUSH_MOUNTED,
            burial_depth_mm=400.0,
            spray_pattern=SprayPattern.FAN,
            spray_angle_deg=120.0,
            spray_range_m=8.0,
            flow_rate_lpm=5.0,
            nozzle_diameter_mm=12.0,
            brine_concentration_percent=23.0,
        ),
    ]

    supply = SupplySystem(
        tank_capacity_l=2000.0,
        pump_pressure_bar=4.0,
        pipe_diameter_mm=50.0,
        pipe_material="HDPE",
        pipe_burial_depth_mm=500.0,  # 이것도 동결심도보다 얕음
        has_heating=False,
        has_insulation=True,
    )

    # 지하 가스관 - SPR-002 근처
    utilities = [
        UndergroundUtility(
            utility_id="GAS-001",
            utility_type="gas",
            depth_mm=500.0,
            position_cross_m=0.2,  # 장치와 매우 가까움!
            diameter_mm=100.0,
        ),
    ]

    return SimulationProject(
        project_id="DEMO-GW-001",
        project_name="강원도 산간도로 염수분사 시스템 평가",
        location_name="Gangwon Mountain Road",
        latitude=37.45,
        longitude=128.90,
        road_segments=[road],
        spray_devices=devices,
        supply_system=supply,
        underground_utilities=utilities,
    )


def create_environment() -> EnvironmentContext:
    """강원도 겨울 야간 환경"""
    return EnvironmentContext(
        location_name="Gangwon Mountain Road",
        latitude=37.45,
        longitude=128.90,
        elevation_m=450.0,
        season=Season.WINTER,
        time_of_day=TimeOfDay.NIGHT,
        climate=KOREA_CLIMATE_PRESETS["gangwon_winter_night"],
        traffic_level=TrafficLevel.LOW,
        is_shaded=False,
        is_wind_exposed=True,
    )


def main():
    print("=" * 70)
    print("  Problem-Driven BIM Simulation Engine")
    print("  Brine Spray System Prototype v0.1")
    print("=" * 70)
    print()

    # 1. 프로젝트 생성
    print("[1/5] Creating simulation project...")
    project = create_project()

    # 2. 환경 구성
    print("[2/5] Setting up environment context...")
    env = create_environment()

    ice_risk = estimate_ice_formation_risk(env.climate)
    print(f"       Ice formation risk: {ice_risk:.0%}")

    # 3. 시뮬레이션 실행
    print("[3/5] Running spray simulation...")
    sim_result = run_full_simulation(project, env, resolution_m=1.0)
    print(f"       Coverage: {sim_result.coverage_ratio:.1%}")
    print(f"       Uncovered zones: {len(sim_result.uncovered_zones)}")

    # 4. 판정 실행
    print("[4/5] Evaluating (Failure-First)...")
    judgment = evaluate(project, env, sim_result)
    print(f"       Verdict: {judgment.verdict.value}")

    # 5. 리포트 생성
    print("[5/5] Generating report...")
    report = generate_report(project, env, sim_result, judgment)

    print()
    print(report)

    # JSON 모델 저장
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_project.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(project.to_json())
    print(f"\nProject JSON saved to: {json_path}")

    # 리포트 저장
    report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
