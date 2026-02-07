"""Neutral Model 데이터 구조 테스트"""

import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.neutral_model import (
    SimulationProject, RoadSegment, RoadType, SurfaceMaterial,
    BrineSprayDevice, SprayPattern, InstallationType,
    SupplySystem, UndergroundUtility,
)


def test_road_segment_creation():
    road = RoadSegment(
        segment_id="TEST-001",
        road_type=RoadType.STRAIGHT,
        surface_material=SurfaceMaterial.ASPHALT,
        length_m=100.0, width_m=3.5, lanes=2,
        slope_percent=0.0, elevation_m=50.0,
    )
    assert road.segment_id == "TEST-001"
    assert road.length_m == 100.0
    assert road.lanes == 2


def test_spray_device_creation():
    device = BrineSprayDevice(
        device_id="SPR-001",
        position_along_road_m=50.0,
        position_cross_m=0.0,
        installation_type=InstallationType.FLUSH_MOUNTED,
        burial_depth_mm=600.0,
        spray_pattern=SprayPattern.FAN,
        spray_angle_deg=120.0,
        spray_range_m=8.0,
        flow_rate_lpm=5.0,
        nozzle_diameter_mm=12.0,
        brine_concentration_percent=23.0,
    )
    assert device.device_id == "SPR-001"
    assert device.spray_range_m == 8.0


def test_project_json_roundtrip():
    project = SimulationProject(
        project_id="JSON-TEST",
        project_name="JSON Roundtrip Test",
        location_name="Test Location",
        latitude=37.0, longitude=127.0,
        road_segments=[
            RoadSegment(
                segment_id="R-001",
                road_type=RoadType.STRAIGHT,
                surface_material=SurfaceMaterial.CONCRETE,
                length_m=50.0, width_m=3.5, lanes=2,
                slope_percent=1.0, elevation_m=100.0,
            )
        ],
        spray_devices=[
            BrineSprayDevice(
                device_id="D-001",
                position_along_road_m=25.0,
                position_cross_m=0.0,
                installation_type=InstallationType.BURIED,
                burial_depth_mm=700.0,
                spray_pattern=SprayPattern.FULL_CIRCLE,
                spray_angle_deg=360.0,
                spray_range_m=10.0,
                flow_rate_lpm=8.0,
                nozzle_diameter_mm=15.0,
                brine_concentration_percent=20.0,
            )
        ],
        supply_system=SupplySystem(
            tank_capacity_l=3000.0,
            pump_pressure_bar=5.0,
            pipe_diameter_mm=50.0,
            pipe_material="HDPE",
            pipe_burial_depth_mm=800.0,
        ),
        underground_utilities=[
            UndergroundUtility(
                utility_id="U-001",
                utility_type="water",
                depth_mm=600.0,
                position_cross_m=1.5,
                diameter_mm=150.0,
            )
        ],
    )

    json_str = project.to_json()
    restored = SimulationProject.from_json(json_str)

    assert restored.project_id == "JSON-TEST"
    assert len(restored.road_segments) == 1
    assert restored.road_segments[0].road_type == RoadType.STRAIGHT
    assert len(restored.spray_devices) == 1
    assert restored.spray_devices[0].spray_pattern == SprayPattern.FULL_CIRCLE
    assert restored.supply_system.tank_capacity_l == 3000.0
    assert len(restored.underground_utilities) == 1
