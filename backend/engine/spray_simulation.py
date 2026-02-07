"""
Spray Simulation Module v0.1
- 염수분사 커버리지 시뮬레이션
- 분사 패턴, 바람 영향, 노면 도달량 계산
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import math

from engine.neutral_model import (
    BrineSprayDevice, RoadSegment, SprayPattern, SimulationProject
)
from engine.gis_reality import (
    EnvironmentContext, estimate_spray_drift
)


@dataclass
class CoverageCell:
    """도로 표면의 단위 셀 (1m x 1m)"""
    x: float  # 도로 방향 위치 (m)
    y: float  # 횡방향 위치 (m)
    brine_amount_gm2: float = 0.0  # 염수 도달량 (g/m²)
    is_covered: bool = False        # 유효 커버리지 여부


@dataclass
class DeviceSimResult:
    """단일 장치의 시뮬레이션 결과"""
    device_id: str
    effective_range_m: float        # 실제 유효 분사 거리
    drift_offset_m: float           # 바람에 의한 편류
    coverage_area_m2: float         # 커버리지 면적
    brine_consumption_lpm: float    # 염수 소모량
    coverage_cells: List[CoverageCell] = field(default_factory=list)


@dataclass
class SimulationResult:
    """전체 시뮬레이션 결과"""
    total_road_area_m2: float
    covered_area_m2: float
    coverage_ratio: float           # 0.0 ~ 1.0
    uncovered_zones: List[Tuple[float, float]]  # 미커버 구간 (시작m, 끝m)
    device_results: List[DeviceSimResult] = field(default_factory=list)
    overlap_area_m2: float = 0.0    # 중복 커버리지 면적
    total_brine_consumption_lph: float = 0.0  # 총 염수 소모량 (L/h)


# ─── 분사 커버리지 계산 핵심 ───

# 유효 분사에 필요한 최소 염수 도달량 (g/m²)
MIN_EFFECTIVE_BRINE_GM2 = 20.0


def calculate_spray_coverage(
    device: BrineSprayDevice,
    road: RoadSegment,
    env: EnvironmentContext,
    resolution_m: float = 1.0,
) -> DeviceSimResult:
    """
    단일 장치의 분사 커버리지를 계산한다.
    """
    # 바람에 의한 편류
    drift = estimate_spray_drift(env.climate.wind_speed_ms, device.spray_range_m)

    # 풍향에 따른 편류 방향 (단순화: 도로 횡방향 성분만)
    wind_cross_component = math.sin(math.radians(env.climate.wind_direction_deg))
    drift_offset = drift * wind_cross_component

    # 온도에 의한 분사 효율 저하
    temp = env.climate.air_temperature_c
    if temp < -10:
        temp_efficiency = 0.7
    elif temp < -5:
        temp_efficiency = 0.85
    elif temp < 0:
        temp_efficiency = 0.95
    else:
        temp_efficiency = 1.0

    effective_range = device.spray_range_m * temp_efficiency

    # 분사 패턴에 따른 커버리지 셀 계산
    cells = []
    half_road = road.width_m * road.lanes / 2.0

    # 분사 영역 생성
    if device.spray_pattern == SprayPattern.LINEAR:
        spray_width = 0.5  # 직선 분사: 좁은 폭
    elif device.spray_pattern == SprayPattern.FAN:
        spray_half_angle = math.radians(device.spray_angle_deg / 2.0)
        spray_width = effective_range * math.tan(spray_half_angle)
    else:  # FULL_CIRCLE
        spray_width = effective_range

    # 그리드 셀 생성 및 염수 도달량 계산
    device_x = device.position_along_road_m
    device_y = device.position_cross_m + drift_offset

    x_start = device_x - effective_range
    x_end = device_x + effective_range
    y_start = device_y - spray_width
    y_end = device_y + spray_width

    for x in _frange(x_start, x_end, resolution_m):
        for y in _frange(y_start, y_end, resolution_m):
            # 도로 범위 내인지 확인
            if x < 0 or x > road.length_m:
                continue
            if abs(y) > half_road:
                continue

            # 장치로부터의 거리
            dist = math.sqrt((x - device_x) ** 2 + (y - device_y) ** 2)
            if dist > effective_range or dist < 0.1:
                continue

            # 거리에 반비례하는 염수 도달량 (단순 모델)
            # 가까울수록 많이, 멀수록 적게
            intensity = 1.0 - (dist / effective_range)
            brine_amount = intensity * device.flow_rate_lpm * 10.0 / max(1, dist ** 1.2)
            brine_amount = max(0, brine_amount)

            is_covered = brine_amount >= MIN_EFFECTIVE_BRINE_GM2
            cells.append(CoverageCell(x=x, y=y, brine_amount_gm2=brine_amount, is_covered=is_covered))

    covered_cells = [c for c in cells if c.is_covered]
    coverage_area = len(covered_cells) * (resolution_m ** 2)

    return DeviceSimResult(
        device_id=device.device_id,
        effective_range_m=effective_range,
        drift_offset_m=drift_offset,
        coverage_area_m2=coverage_area,
        brine_consumption_lpm=device.flow_rate_lpm,
        coverage_cells=cells,
    )


def run_full_simulation(
    project: SimulationProject,
    env: EnvironmentContext,
    resolution_m: float = 1.0,
) -> SimulationResult:
    """
    전체 프로젝트에 대한 시뮬레이션을 실행한다.
    """
    if not project.road_segments:
        raise ValueError("시뮬레이션 실행에 도로 구간이 필요합니다.")
    if not project.spray_devices:
        raise ValueError("시뮬레이션 실행에 분사 장치가 필요합니다.")

    road = project.road_segments[0]  # 프로토타입: 단일 구간
    total_road_area = road.length_m * road.width_m * road.lanes

    device_results = []
    all_covered_positions = set()
    all_road_positions = set()

    # 전체 도로 그리드
    half_road = road.width_m * road.lanes / 2.0
    for x in _frange(0, road.length_m, resolution_m):
        for y in _frange(-half_road, half_road, resolution_m):
            all_road_positions.add((round(x, 1), round(y, 1)))

    overlap_count = 0

    for device in project.spray_devices:
        result = calculate_spray_coverage(device, road, env, resolution_m)
        device_results.append(result)

        for cell in result.coverage_cells:
            if cell.is_covered:
                pos = (round(cell.x, 1), round(cell.y, 1))
                if pos in all_covered_positions:
                    overlap_count += 1
                all_covered_positions.add(pos)

    covered_area = len(all_covered_positions) * (resolution_m ** 2)
    coverage_ratio = covered_area / total_road_area if total_road_area > 0 else 0

    # 미커버 구간 탐지
    uncovered = all_road_positions - all_covered_positions
    uncovered_zones = _find_uncovered_zones(uncovered, road.length_m, resolution_m)

    total_consumption = sum(d.brine_consumption_lpm for d in device_results) * 60

    return SimulationResult(
        total_road_area_m2=total_road_area,
        covered_area_m2=covered_area,
        coverage_ratio=coverage_ratio,
        uncovered_zones=uncovered_zones,
        device_results=device_results,
        overlap_area_m2=overlap_count * (resolution_m ** 2),
        total_brine_consumption_lph=total_consumption,
    )


def _frange(start: float, stop: float, step: float):
    """float range generator"""
    current = start
    while current < stop:
        yield round(current, 4)
        current += step


def _find_uncovered_zones(
    uncovered_positions: set,
    road_length: float,
    resolution: float,
) -> List[Tuple[float, float]]:
    """미커버 구간을 연속 구간으로 묶는다."""
    if not uncovered_positions:
        return []

    x_positions = sorted(set(pos[0] for pos in uncovered_positions))
    if not x_positions:
        return []

    zones = []
    zone_start = x_positions[0]
    prev_x = x_positions[0]

    for x in x_positions[1:]:
        if x - prev_x > resolution * 1.5:  # 불연속
            zones.append((zone_start, prev_x))
            zone_start = x
        prev_x = x

    zones.append((zone_start, prev_x))
    return zones
