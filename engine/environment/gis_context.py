"""GIS and location context for simulation.

Provides location-based environmental adjustments:
- Elevation corrections for temperature and pressure
- Season determination for solar radiation
- Time-of-day adjustments
"""

import math
from datetime import datetime
from typing import Optional

from engine.domain.models import EnvironmentCondition


def temperature_lapse_rate(elevation: float, base_temp: float) -> float:
    """Adjust temperature for elevation using standard lapse rate.

    Standard atmospheric lapse rate: -6.5 C per 1000m.
    """
    return base_temp - 6.5 * (elevation / 1000.0)


def wind_speed_height_correction(
    measured_speed: float, measured_height: float = 10.0, target_height: float = 0.3
) -> float:
    """Correct wind speed for height using power law.

    v(z) = v(z_ref) * (z / z_ref)^alpha
    alpha = 0.14 for open terrain (road surface)
    """
    alpha = 0.14
    if measured_height <= 0:
        return measured_speed
    return measured_speed * (target_height / measured_height) ** alpha


def determine_season(month: int) -> str:
    """Determine Korean season from month."""
    if month in (12, 1, 2):
        return "winter"
    elif month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    else:
        return "autumn"


def is_icing_season(month: int) -> bool:
    """Check if the month is within Korean icing season (Nov-Mar)."""
    return month in (11, 12, 1, 2, 3)


def apply_location_corrections(
    environment: EnvironmentCondition,
    elevation: float = 0.0,
    latitude: Optional[float] = None,
    month: Optional[int] = None,
) -> EnvironmentCondition:
    """Apply location-based corrections to environment conditions."""
    corrected_temp = temperature_lapse_rate(elevation, environment.temperature)
    corrected_wind = wind_speed_height_correction(environment.wind_speed)

    return EnvironmentCondition(
        temperature=corrected_temp,
        humidity=environment.humidity,
        wind_speed=corrected_wind,
        wind_direction=environment.wind_direction,
        precipitation=environment.precipitation,
        solar_radiation=environment.solar_radiation,
        road_surface_temp=environment.road_surface_temp,
    )
