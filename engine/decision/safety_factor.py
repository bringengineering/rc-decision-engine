"""Safety factor computation module.

SF = capacity / demand

For different simulation types:
- Salt spray: capacity = effective brine coverage, demand = KDS minimum
- Thermal: capacity = temperature margin above freezing
- Structural: capacity = material strength, demand = applied load
"""

from engine.domain.constants import (
    KDS_MIN_BRINE_COVERAGE,
    KDS_MIN_SAFETY_FACTOR,
    FREEZING_POINT_WATER,
)


def compute_spray_safety_factor(
    coverage_ratio: float, required: float = KDS_MIN_BRINE_COVERAGE
) -> float:
    """SF for spray coverage: actual / required."""
    if required <= 0:
        return float("inf")
    return coverage_ratio / required


def compute_thermal_safety_factor(
    surface_temp: float, freezing_point: float, reference_margin: float = 3.33
) -> float:
    """SF for thermal: temperature margin / reference margin."""
    margin = surface_temp - freezing_point
    if reference_margin <= 0:
        return 0.0
    return max(margin / reference_margin, 0.0)


def compute_combined_safety_factor(
    spray_sf: float, thermal_sf: float, weights: tuple[float, float] = (0.6, 0.4)
) -> float:
    """Weighted combination of spray and thermal safety factors."""
    return spray_sf * weights[0] + thermal_sf * weights[1]
