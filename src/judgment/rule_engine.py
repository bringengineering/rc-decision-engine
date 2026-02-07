"""
L0 Rule-Based Judgment Engine v0.1
- 규칙 기반 PASS / FAIL / CONDITIONAL PASS 판정
- Failure-First 원칙: 실패부터 평가
"""

from dataclasses import dataclass, field
from typing import List
from enum import Enum

from src.models.neutral_model import (
    SimulationProject, InstallationType, BrineSprayDevice, UndergroundUtility
)
from src.layers.gis_reality import EnvironmentContext, estimate_ice_formation_risk
from src.simulation.spray_simulation import SimulationResult


class Verdict(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    CONDITIONAL_PASS = "CONDITIONAL_PASS"


class Severity(str, Enum):
    CRITICAL = "critical"     # 즉시 실패
    WARNING = "warning"       # 조건부 통과 가능
    INFO = "info"             # 참고 사항


@dataclass
class FailureObservation:
    """관찰된 실패/위험 요소"""
    rule_id: str
    category: str
    severity: Severity
    description: str
    evidence: str
    recommendation: str = ""


@dataclass
class JudgmentResult:
    """최종 판정 결과"""
    verdict: Verdict
    confidence: float  # 판정 신뢰도 (0.0 ~ 1.0)
    summary: str
    failures: List[FailureObservation] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)  # CONDITIONAL일 때 조건 목록
    limitations: List[str] = field(default_factory=list)


# ─── 판정 규칙 정의 ───

# 최소 커버리지 비율 (80% 이상이어야 유효)
MIN_COVERAGE_RATIO = 0.80

# 최대 미커버 연속 구간 (m)
MAX_UNCOVERED_GAP_M = 10.0

# 매립 장치와 지하 매설물 간 최소 이격 거리 (mm)
MIN_UTILITY_CLEARANCE_MM = 300.0

# 동파 위험 매립 깊이 한계 (mm) - 지역 동결심도 기준
FROST_DEPTH_LIMITS = {
    "seoul": 600,
    "gangwon": 900,
    "busan": 300,
    "daejeon": 500,
    "default": 600,
}


def evaluate(
    project: SimulationProject,
    env: EnvironmentContext,
    sim_result: SimulationResult,
) -> JudgmentResult:
    """
    Failure-First 판정을 실행한다.
    모든 실패 가능성을 먼저 탐색한 후, 최종 판정을 내린다.
    """
    failures: List[FailureObservation] = []

    # ── Rule 1: 커버리지 부족 ──
    failures.extend(_check_coverage(sim_result))

    # ── Rule 2: 미커버 연속 구간 ──
    failures.extend(_check_uncovered_gaps(sim_result))

    # ── Rule 3: 바람에 의한 분사 편류 ──
    failures.extend(_check_wind_drift(sim_result, env))

    # ── Rule 4: 동파 위험 ──
    failures.extend(_check_frost_risk(project, env))

    # ── Rule 5: 지하 매설물 간섭 ──
    failures.extend(_check_utility_conflict(project))

    # ── Rule 6: 염수 소모량 대비 탱크 용량 ──
    failures.extend(_check_supply_capacity(project, sim_result))

    # ── Rule 7: 경사면 분사 유효성 ──
    failures.extend(_check_slope_effectiveness(project, env))

    # ── 최종 판정 ──
    return _make_verdict(failures)


def _check_coverage(sim: SimulationResult) -> List[FailureObservation]:
    obs = []
    if sim.coverage_ratio < 0.5:
        obs.append(FailureObservation(
            rule_id="COV-001",
            category="커버리지",
            severity=Severity.CRITICAL,
            description="분사 커버리지가 심각하게 부족합니다.",
            evidence=f"커버리지 비율: {sim.coverage_ratio:.1%} (기준: {MIN_COVERAGE_RATIO:.0%} 이상)",
            recommendation="장치 수를 늘리거나 배치 간격을 줄여야 합니다.",
        ))
    elif sim.coverage_ratio < MIN_COVERAGE_RATIO:
        obs.append(FailureObservation(
            rule_id="COV-002",
            category="커버리지",
            severity=Severity.WARNING,
            description="분사 커버리지가 기준 미달입니다.",
            evidence=f"커버리지 비율: {sim.coverage_ratio:.1%} (기준: {MIN_COVERAGE_RATIO:.0%} 이상)",
            recommendation="장치 위치 조정 또는 분사 각도 확대를 검토하세요.",
        ))
    return obs


def _check_uncovered_gaps(sim: SimulationResult) -> List[FailureObservation]:
    obs = []
    for start, end in sim.uncovered_zones:
        gap = end - start
        if gap > MAX_UNCOVERED_GAP_M:
            obs.append(FailureObservation(
                rule_id="GAP-001",
                category="미커버 구간",
                severity=Severity.CRITICAL,
                description=f"연속 미커버 구간이 {gap:.1f}m로 허용치를 초과합니다.",
                evidence=f"구간: {start:.1f}m ~ {end:.1f}m (허용: {MAX_UNCOVERED_GAP_M}m 이하)",
                recommendation="해당 구간에 추가 장치 설치가 필요합니다.",
            ))
        elif gap > MAX_UNCOVERED_GAP_M * 0.7:
            obs.append(FailureObservation(
                rule_id="GAP-002",
                category="미커버 구간",
                severity=Severity.WARNING,
                description=f"연속 미커버 구간이 {gap:.1f}m로 주의가 필요합니다.",
                evidence=f"구간: {start:.1f}m ~ {end:.1f}m",
                recommendation="장치 간격 재검토를 권장합니다.",
            ))
    return obs


def _check_wind_drift(sim: SimulationResult, env: EnvironmentContext) -> List[FailureObservation]:
    obs = []
    for dr in sim.device_results:
        if abs(dr.drift_offset_m) > dr.effective_range_m * 0.3:
            obs.append(FailureObservation(
                rule_id="WIND-001",
                category="바람 영향",
                severity=Severity.WARNING,
                description=f"장치 {dr.device_id}의 분사가 바람에 의해 크게 편류됩니다.",
                evidence=f"편류: {dr.drift_offset_m:.2f}m (풍속: {env.climate.wind_speed_ms}m/s)",
                recommendation="방풍 커버 설치 또는 분사 방향 조정을 검토하세요.",
            ))
    return obs


def _check_frost_risk(project: SimulationProject, env: EnvironmentContext) -> List[FailureObservation]:
    obs = []
    # 지역별 동결심도 추정
    region = "default"
    loc_lower = env.location_name.lower()
    for key in FROST_DEPTH_LIMITS:
        if key in loc_lower:
            region = key
            break
    frost_depth = FROST_DEPTH_LIMITS[region]

    for device in project.spray_devices:
        if device.burial_depth_mm > 0 and device.burial_depth_mm < frost_depth:
            obs.append(FailureObservation(
                rule_id="FROST-001",
                category="동파 위험",
                severity=Severity.CRITICAL,
                description=f"장치 {device.device_id}의 매립 깊이가 동결심도보다 얕습니다.",
                evidence=f"매립: {device.burial_depth_mm}mm, 동결심도: {frost_depth}mm ({region})",
                recommendation=f"매립 깊이를 {frost_depth}mm 이상으로 하거나 히팅 시스템을 추가하세요.",
            ))

    # 배관 동파 확인
    if project.supply_system:
        ss = project.supply_system
        if ss.pipe_burial_depth_mm < frost_depth and not ss.has_heating:
            obs.append(FailureObservation(
                rule_id="FROST-002",
                category="동파 위험",
                severity=Severity.CRITICAL,
                description="공급 배관이 동결심도보다 얕고 히팅이 없습니다.",
                evidence=f"배관 매립: {ss.pipe_burial_depth_mm}mm, 동결심도: {frost_depth}mm",
                recommendation="배관 히팅 또는 단열 추가, 또는 매립 깊이 증가가 필요합니다.",
            ))
    return obs


def _check_utility_conflict(project: SimulationProject) -> List[FailureObservation]:
    obs = []
    for device in project.spray_devices:
        if device.burial_depth_mm == 0:
            continue
        for util in project.underground_utilities:
            # 횡방향 거리 확인
            cross_dist = abs(device.position_cross_m - util.position_cross_m)
            depth_dist = abs(device.burial_depth_mm - util.depth_mm)
            clearance = min(cross_dist * 1000, depth_dist)  # mm 단위 비교

            if clearance < MIN_UTILITY_CLEARANCE_MM:
                obs.append(FailureObservation(
                    rule_id="UTIL-001",
                    category="지하 매설물 간섭",
                    severity=Severity.CRITICAL,
                    description=f"장치 {device.device_id}가 {util.utility_type} 매설물과 간섭합니다.",
                    evidence=f"이격: {clearance:.0f}mm (최소: {MIN_UTILITY_CLEARANCE_MM}mm)",
                    recommendation="장치 위치를 이동하거나 매설물 이설을 검토하세요.",
                ))
    return obs


def _check_supply_capacity(project: SimulationProject, sim: SimulationResult) -> List[FailureObservation]:
    obs = []
    if not project.supply_system:
        obs.append(FailureObservation(
            rule_id="SUP-001",
            category="공급 시스템",
            severity=Severity.WARNING,
            description="공급 시스템이 정의되지 않았습니다.",
            evidence="탱크 용량, 펌프 압력 등을 확인할 수 없습니다.",
            recommendation="공급 시스템 사양을 입력하세요.",
        ))
        return obs

    tank = project.supply_system.tank_capacity_l
    consumption_lph = sim.total_brine_consumption_lph
    if consumption_lph > 0:
        runtime_hours = tank / consumption_lph
        if runtime_hours < 2.0:
            obs.append(FailureObservation(
                rule_id="SUP-002",
                category="공급 시스템",
                severity=Severity.WARNING,
                description=f"탱크 용량 대비 운영 시간이 {runtime_hours:.1f}시간으로 짧습니다.",
                evidence=f"탱크: {tank}L, 소모: {consumption_lph:.0f}L/h",
                recommendation="탱크 용량 증가 또는 자동 보충 시스템을 검토하세요.",
            ))
    return obs


def _check_slope_effectiveness(project: SimulationProject, env: EnvironmentContext) -> List[FailureObservation]:
    obs = []
    for road in project.road_segments:
        if abs(road.slope_percent) > 5.0:
            obs.append(FailureObservation(
                rule_id="SLOPE-001",
                category="경사면 효과",
                severity=Severity.WARNING,
                description=f"경사도 {road.slope_percent}%에서 염수 흐름 편향이 예상됩니다.",
                evidence=f"구간 {road.segment_id}: 경사 {road.slope_percent}%",
                recommendation="경사 하류 방향에 추가 분사 지점을 검토하세요.",
            ))
    return obs


def _make_verdict(failures: List[FailureObservation]) -> JudgmentResult:
    """실패 관찰 결과를 종합하여 최종 판정을 내린다."""
    critical = [f for f in failures if f.severity == Severity.CRITICAL]
    warnings = [f for f in failures if f.severity == Severity.WARNING]

    if critical:
        return JudgmentResult(
            verdict=Verdict.FAIL,
            confidence=0.9,
            summary=f"{len(critical)}건의 심각한 문제가 발견되었습니다. "
                    f"현재 설계로는 현실 조건에서 실패할 가능성이 높습니다.",
            failures=failures,
            limitations=[
                "이 판정은 L0 규칙 기반 시뮬레이션 결과입니다.",
                "실제 물리 시뮬레이션(L1/L2)은 수행되지 않았습니다.",
                "현장 조건에 따라 결과가 달라질 수 있습니다.",
            ],
        )
    elif warnings:
        conditions = [w.recommendation for w in warnings if w.recommendation]
        return JudgmentResult(
            verdict=Verdict.CONDITIONAL_PASS,
            confidence=0.7,
            summary=f"{len(warnings)}건의 주의 사항이 있습니다. "
                    f"아래 조건이 충족되면 운영 가능합니다.",
            failures=failures,
            conditions=conditions,
            limitations=[
                "이 판정은 L0 규칙 기반 시뮬레이션 결과입니다.",
                "실제 물리 시뮬레이션(L1/L2)은 수행되지 않았습니다.",
                "현장 조건에 따라 결과가 달라질 수 있습니다.",
            ],
        )
    else:
        return JudgmentResult(
            verdict=Verdict.PASS,
            confidence=0.8,
            summary="현재 설계는 시뮬레이션된 환경 조건에서 유효하게 동작합니다.",
            failures=failures,
            limitations=[
                "이 판정은 L0 규칙 기반 시뮬레이션 결과입니다.",
                "실제 물리 시뮬레이션(L1/L2)은 수행되지 않았습니다.",
                "현장 조건에 따라 결과가 달라질 수 있습니다.",
                "극한 기후 조건은 별도 시뮬레이션이 필요합니다.",
            ],
        )
