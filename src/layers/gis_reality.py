"""
GIS Reality Layer v0.1
- 위치 기반 환경 조건 생성
- 기후, 계절, 시간대, 교통 맥락
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
import json
import math


class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


class TimeOfDay(str, Enum):
    DAWN = "dawn"           # 04-07
    MORNING = "morning"     # 07-12
    AFTERNOON = "afternoon" # 12-17
    EVENING = "evening"     # 17-21
    NIGHT = "night"         # 21-04


class TrafficLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CONGESTED = "congested"


@dataclass
class ClimateCondition:
    """특정 시점의 기후 조건"""
    air_temperature_c: float        # 기온 (°C)
    road_surface_temperature_c: float  # 노면 온도 (°C)
    humidity_percent: float         # 상대 습도 (%)
    wind_speed_ms: float            # 풍속 (m/s)
    wind_direction_deg: float       # 풍향 (도, 북=0)
    precipitation_type: str         # none, rain, snow, sleet, freezing_rain
    precipitation_intensity_mmh: float  # 강수량 (mm/h)
    solar_radiation_wm2: float      # 일사량 (W/m²)
    cloud_cover_percent: float      # 운량 (%)


@dataclass
class EnvironmentContext:
    """시뮬레이션 환경 전체 컨텍스트"""
    location_name: str
    latitude: float
    longitude: float
    elevation_m: float
    season: Season
    time_of_day: TimeOfDay
    climate: ClimateCondition
    traffic_level: TrafficLevel
    is_shaded: bool = False         # 그늘 여부 (교량 하부 등)
    is_wind_exposed: bool = True    # 바람 노출 여부

    def to_json(self, indent=2) -> str:
        return json.dumps(asdict(self), indent=indent, ensure_ascii=False)


# ─── 한국 주요 도시 기후 프리셋 ───

KOREA_CLIMATE_PRESETS = {
    "seoul_winter_night": ClimateCondition(
        air_temperature_c=-8.0,
        road_surface_temperature_c=-10.0,
        humidity_percent=65.0,
        wind_speed_ms=3.5,
        wind_direction_deg=315.0,
        precipitation_type="snow",
        precipitation_intensity_mmh=2.0,
        solar_radiation_wm2=0.0,
        cloud_cover_percent=90.0,
    ),
    "seoul_winter_dawn": ClimateCondition(
        air_temperature_c=-12.0,
        road_surface_temperature_c=-15.0,
        humidity_percent=70.0,
        wind_speed_ms=1.5,
        wind_direction_deg=0.0,
        precipitation_type="none",
        precipitation_intensity_mmh=0.0,
        solar_radiation_wm2=0.0,
        cloud_cover_percent=30.0,
    ),
    "gangwon_winter_night": ClimateCondition(
        air_temperature_c=-15.0,
        road_surface_temperature_c=-18.0,
        humidity_percent=75.0,
        wind_speed_ms=5.0,
        wind_direction_deg=270.0,
        precipitation_type="snow",
        precipitation_intensity_mmh=5.0,
        solar_radiation_wm2=0.0,
        cloud_cover_percent=95.0,
    ),
    "busan_winter_morning": ClimateCondition(
        air_temperature_c=-2.0,
        road_surface_temperature_c=-3.0,
        humidity_percent=80.0,
        wind_speed_ms=6.0,
        wind_direction_deg=180.0,
        precipitation_type="freezing_rain",
        precipitation_intensity_mmh=1.5,
        solar_radiation_wm2=50.0,
        cloud_cover_percent=80.0,
    ),
    "daejeon_winter_dawn": ClimateCondition(
        air_temperature_c=-6.0,
        road_surface_temperature_c=-9.0,
        humidity_percent=60.0,
        wind_speed_ms=2.0,
        wind_direction_deg=0.0,
        precipitation_type="none",
        precipitation_intensity_mmh=0.0,
        solar_radiation_wm2=0.0,
        cloud_cover_percent=20.0,
    ),
}


def estimate_ice_formation_risk(climate: ClimateCondition) -> float:
    """
    결빙 위험도 추정 (0.0 ~ 1.0)
    규칙 기반 단순 모델
    """
    risk = 0.0

    # 노면 온도가 0도 이하면 기본 위험
    if climate.road_surface_temperature_c <= 0:
        risk += 0.4
        # 온도가 낮을수록 위험 증가
        risk += min(0.3, abs(climate.road_surface_temperature_c) * 0.02)

    # 습도가 높으면 위험 증가
    if climate.humidity_percent > 70:
        risk += 0.1

    # 강수가 있으면 위험 증가
    if climate.precipitation_type in ("snow", "sleet", "freezing_rain"):
        risk += 0.2
    elif climate.precipitation_type == "rain" and climate.road_surface_temperature_c <= 1:
        risk += 0.15

    # 바람이 약하면 (방사냉각) 위험 증가
    if climate.wind_speed_ms < 2.0 and climate.cloud_cover_percent < 30:
        risk += 0.1

    return min(1.0, risk)


def estimate_spray_drift(wind_speed_ms: float, spray_range_m: float) -> float:
    """
    바람에 의한 분사 편류 추정 (m)
    분사 도달 거리와 풍속에 비례하는 단순 모델
    """
    # 경험적 계수: 풍속 1m/s당 분사거리의 5% 편류
    drift_factor = 0.05
    return wind_speed_ms * spray_range_m * drift_factor
