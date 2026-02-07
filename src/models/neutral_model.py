"""
Neutral Model Schema v0.1
- 염수분사장치 시뮬레이션을 위한 중립 데이터 모델
- BIM/CAD 독립적, JSON 직렬화 가능
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
from enum import Enum
import json


# ─── 도로 구간 모델 ───

class RoadType(str, Enum):
    STRAIGHT = "straight"
    CURVE = "curve"
    BRIDGE = "bridge"
    OVERPASS = "overpass"
    UNDERPASS = "underpass"
    RAMP = "ramp"
    INTERSECTION = "intersection"


class SurfaceMaterial(str, Enum):
    ASPHALT = "asphalt"
    CONCRETE = "concrete"
    STEEL_DECK = "steel_deck"


@dataclass
class RoadSegment:
    """도로 구간 정의"""
    segment_id: str
    road_type: RoadType
    surface_material: SurfaceMaterial
    length_m: float          # 구간 길이 (m)
    width_m: float           # 차로 폭 (m)
    lanes: int               # 차로 수
    slope_percent: float     # 경사도 (%)
    elevation_m: float       # 해발 고도 (m)
    has_median: bool = False
    has_shoulder: bool = True
    shoulder_width_m: float = 2.0


# ─── 염수분사장치 모델 ───

class SprayPattern(str, Enum):
    LINEAR = "linear"        # 직선 분사
    FAN = "fan"              # 부채꼴 분사
    FULL_CIRCLE = "full_circle"  # 360도 분사


class InstallationType(str, Enum):
    SURFACE_MOUNTED = "surface_mounted"   # 노면 위 설치
    FLUSH_MOUNTED = "flush_mounted"       # 노면과 수평 매립
    BURIED = "buried"                     # 완전 매립


@dataclass
class BrineSprayDevice:
    """염수분사장치 단일 유닛"""
    device_id: str
    position_along_road_m: float   # 도로 시작점부터 거리 (m)
    position_cross_m: float        # 도로 중앙선에서 횡방향 거리 (m)
    installation_type: InstallationType
    burial_depth_mm: float         # 매립 깊이 (mm), 0이면 노면 설치
    spray_pattern: SprayPattern
    spray_angle_deg: float         # 분사 각도 (도)
    spray_range_m: float           # 분사 도달 거리 (m)
    flow_rate_lpm: float           # 유량 (L/min)
    nozzle_diameter_mm: float      # 노즐 직경 (mm)
    brine_concentration_percent: float  # 염수 농도 (%)


@dataclass
class SupplySystem:
    """염수 공급 시스템"""
    tank_capacity_l: float         # 탱크 용량 (L)
    pump_pressure_bar: float       # 펌프 압력 (bar)
    pipe_diameter_mm: float        # 배관 직경 (mm)
    pipe_material: str             # 배관 재질
    pipe_burial_depth_mm: float    # 배관 매립 깊이 (mm)
    has_heating: bool = False      # 배관 히팅 여부
    has_insulation: bool = False   # 단열 여부


# ─── 지하 매설물 제약 ───

@dataclass
class UndergroundUtility:
    """지하 매설물"""
    utility_id: str
    utility_type: str        # gas, water, electric, telecom, sewer
    depth_mm: float          # 매설 깊이 (mm)
    position_cross_m: float  # 도로 중앙선에서 횡방향 거리 (m)
    diameter_mm: float       # 관 직경 (mm)


# ─── 프로젝트 최상위 모델 ───

@dataclass
class SimulationProject:
    """시뮬레이션 프로젝트 전체 모델"""
    schema_version: str = "0.1.0"
    project_id: str = ""
    project_name: str = ""
    location_name: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    road_segments: List[RoadSegment] = field(default_factory=list)
    spray_devices: List[BrineSprayDevice] = field(default_factory=list)
    supply_system: Optional[SupplySystem] = None
    underground_utilities: List[UndergroundUtility] = field(default_factory=list)

    def to_json(self, indent=2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "SimulationProject":
        data = json.loads(json_str)
        # Reconstruct nested objects
        data["road_segments"] = [
            RoadSegment(**{**seg, "road_type": RoadType(seg["road_type"]),
                          "surface_material": SurfaceMaterial(seg["surface_material"])})
            for seg in data.get("road_segments", [])
        ]
        data["spray_devices"] = [
            BrineSprayDevice(**{**dev,
                               "installation_type": InstallationType(dev["installation_type"]),
                               "spray_pattern": SprayPattern(dev["spray_pattern"])})
            for dev in data.get("spray_devices", [])
        ]
        if data.get("supply_system"):
            data["supply_system"] = SupplySystem(**data["supply_system"])
        data["underground_utilities"] = [
            UndergroundUtility(**u) for u in data.get("underground_utilities", [])
        ]
        return cls(**data)
