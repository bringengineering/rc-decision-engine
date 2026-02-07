"""
Judgment Report Generator v0.1
- 판정 결과를 구조화된 텍스트 리포트로 출력
- 감사 가능한 형태
"""

from datetime import datetime
from engine.neutral_model import SimulationProject
from engine.gis_reality import EnvironmentContext, estimate_ice_formation_risk
from engine.spray_simulation import SimulationResult
from engine.rule_engine import JudgmentResult, Verdict, Severity


def generate_report(
    project: SimulationProject,
    env: EnvironmentContext,
    sim_result: SimulationResult,
    judgment: JudgmentResult,
) -> str:
    """판정 보고서를 생성한다."""

    ice_risk = estimate_ice_formation_risk(env.climate)

    verdict_symbol = {
        Verdict.PASS: "[PASS]",
        Verdict.FAIL: "[FAIL]",
        Verdict.CONDITIONAL_PASS: "[CONDITIONAL PASS]",
    }

    lines = []
    lines.append("=" * 70)
    lines.append("  BRINE SPRAY SYSTEM - SIMULATION JUDGMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"  Report Date  : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"  Project      : {project.project_name}")
    lines.append(f"  Project ID   : {project.project_id}")
    lines.append(f"  Schema Ver.  : {project.schema_version}")
    lines.append("")

    # ── 1. Executive Judgment Summary ──
    lines.append("-" * 70)
    lines.append("  1. EXECUTIVE JUDGMENT SUMMARY")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"  VERDICT : {verdict_symbol[judgment.verdict]}")
    lines.append(f"  Confidence : {judgment.confidence:.0%}")
    lines.append(f"  Summary : {judgment.summary}")
    lines.append("")

    # ── 2. Simulation Environment ──
    lines.append("-" * 70)
    lines.append("  2. SIMULATION ENVIRONMENT")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"  Location     : {env.location_name}")
    lines.append(f"  Coordinates  : {env.latitude:.4f}, {env.longitude:.4f}")
    lines.append(f"  Elevation    : {env.elevation_m:.0f}m")
    lines.append(f"  Season       : {env.season.value}")
    lines.append(f"  Time of Day  : {env.time_of_day.value}")
    lines.append(f"  Traffic      : {env.traffic_level.value}")
    lines.append("")
    lines.append(f"  Air Temp     : {env.climate.air_temperature_c:.1f} C")
    lines.append(f"  Road Temp    : {env.climate.road_surface_temperature_c:.1f} C")
    lines.append(f"  Humidity     : {env.climate.humidity_percent:.0f}%")
    lines.append(f"  Wind         : {env.climate.wind_speed_ms:.1f} m/s @ {env.climate.wind_direction_deg:.0f} deg")
    lines.append(f"  Precipitation: {env.climate.precipitation_type} ({env.climate.precipitation_intensity_mmh:.1f} mm/h)")
    lines.append(f"  Ice Risk     : {ice_risk:.0%}")
    lines.append("")

    # ── 3. Installation Overview ──
    lines.append("-" * 70)
    lines.append("  3. INSTALLATION OVERVIEW")
    lines.append("-" * 70)
    lines.append("")
    for road in project.road_segments:
        lines.append(f"  Road: {road.segment_id}")
        lines.append(f"    Type     : {road.road_type.value}")
        lines.append(f"    Length   : {road.length_m:.0f}m x {road.width_m:.1f}m x {road.lanes} lanes")
        lines.append(f"    Surface  : {road.surface_material.value}")
        lines.append(f"    Slope    : {road.slope_percent:.1f}%")
        lines.append("")

    lines.append(f"  Spray Devices: {len(project.spray_devices)} units")
    for dev in project.spray_devices:
        lines.append(f"    [{dev.device_id}] @ {dev.position_along_road_m:.0f}m, "
                     f"pattern={dev.spray_pattern.value}, "
                     f"range={dev.spray_range_m:.1f}m, "
                     f"buried={dev.burial_depth_mm:.0f}mm")
    lines.append("")

    # ── 4. Simulation Results ──
    lines.append("-" * 70)
    lines.append("  4. SIMULATION RESULTS")
    lines.append("-" * 70)
    lines.append("")
    lines.append(f"  Total Road Area    : {sim_result.total_road_area_m2:.0f} m2")
    lines.append(f"  Covered Area       : {sim_result.covered_area_m2:.0f} m2")
    lines.append(f"  Coverage Ratio     : {sim_result.coverage_ratio:.1%}")
    lines.append(f"  Overlap Area       : {sim_result.overlap_area_m2:.0f} m2")
    lines.append(f"  Brine Consumption  : {sim_result.total_brine_consumption_lph:.0f} L/h")
    lines.append("")

    if sim_result.uncovered_zones:
        lines.append("  Uncovered Zones:")
        for start, end in sim_result.uncovered_zones:
            lines.append(f"    {start:.0f}m ~ {end:.0f}m ({end - start:.0f}m)")
    else:
        lines.append("  Uncovered Zones: None")
    lines.append("")

    # ── 5. Failure Observations ──
    lines.append("-" * 70)
    lines.append("  5. FAILURE OBSERVATIONS")
    lines.append("-" * 70)
    lines.append("")

    if not judgment.failures:
        lines.append("  No failures observed.")
    else:
        for i, f in enumerate(judgment.failures, 1):
            icon = "!!" if f.severity == Severity.CRITICAL else "!"
            lines.append(f"  [{icon}] {f.rule_id} - {f.category} ({f.severity.value})")
            lines.append(f"      {f.description}")
            lines.append(f"      Evidence: {f.evidence}")
            if f.recommendation:
                lines.append(f"      Action: {f.recommendation}")
            lines.append("")

    # ── 6. Conditions (if CONDITIONAL PASS) ──
    if judgment.conditions:
        lines.append("-" * 70)
        lines.append("  6. CONDITIONS FOR PASS")
        lines.append("-" * 70)
        lines.append("")
        for i, cond in enumerate(judgment.conditions, 1):
            lines.append(f"  {i}. {cond}")
        lines.append("")

    # ── 7. Limitations & Disclaimer ──
    lines.append("-" * 70)
    lines.append("  7. LIMITATIONS & DISCLAIMER")
    lines.append("-" * 70)
    lines.append("")
    for lim in judgment.limitations:
        lines.append(f"  - {lim}")
    lines.append("")
    lines.append("  IMPORTANT:")
    lines.append("  This report provides JUDGMENT INFORMATION only.")
    lines.append("  All DECISIONS and ACCOUNTABILITY remain with qualified engineers.")
    lines.append("  This system does not design, decide, or replace professional judgment.")
    lines.append("")
    lines.append("=" * 70)
    lines.append("  END OF REPORT")
    lines.append("=" * 70)

    return "\n".join(lines)
