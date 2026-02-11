"""Korean climate presets and environmental context.

Provides predefined climate conditions for major Korean regions
used in simulation when real sensor data is not available.
"""

from engine.domain.models import ClimatePreset, EnvironmentCondition

CLIMATE_PRESETS: dict[str, dict] = {
    "gangwon_winter_severe": {
        "name": "Gangwon Winter (Severe)",
        "region": "Gangwon-do",
        "conditions": {
            "temperature": -15.0,
            "humidity": 65.0,
            "wind_speed": 8.0,
            "wind_direction": 315.0,
            "precipitation": 5.0,
            "solar_radiation": 50.0,
        },
    },
    "gangwon_winter_moderate": {
        "name": "Gangwon Winter (Moderate)",
        "region": "Gangwon-do",
        "conditions": {
            "temperature": -5.0,
            "humidity": 70.0,
            "wind_speed": 4.0,
            "wind_direction": 270.0,
            "precipitation": 2.0,
            "solar_radiation": 100.0,
        },
    },
    "seoul_winter": {
        "name": "Seoul Winter",
        "region": "Seoul",
        "conditions": {
            "temperature": -8.0,
            "humidity": 55.0,
            "wind_speed": 5.0,
            "wind_direction": 300.0,
            "precipitation": 1.0,
            "solar_radiation": 120.0,
        },
    },
    "gyeongbu_expressway_winter": {
        "name": "Gyeongbu Expressway Winter",
        "region": "Chungcheong-do",
        "conditions": {
            "temperature": -3.0,
            "humidity": 75.0,
            "wind_speed": 6.0,
            "wind_direction": 250.0,
            "precipitation": 3.0,
            "solar_radiation": 80.0,
        },
    },
    "yeongdong_expressway_winter": {
        "name": "Yeongdong Expressway Winter",
        "region": "Gangwon-do",
        "conditions": {
            "temperature": -12.0,
            "humidity": 80.0,
            "wind_speed": 10.0,
            "wind_direction": 0.0,
            "precipitation": 8.0,
            "solar_radiation": 30.0,
        },
    },
    "busan_winter": {
        "name": "Busan Winter",
        "region": "Busan",
        "conditions": {
            "temperature": 0.0,
            "humidity": 60.0,
            "wind_speed": 7.0,
            "wind_direction": 180.0,
            "precipitation": 0.5,
            "solar_radiation": 150.0,
        },
    },
    "spring_transition": {
        "name": "Spring Transition (March)",
        "region": "National",
        "conditions": {
            "temperature": 5.0,
            "humidity": 50.0,
            "wind_speed": 3.0,
            "wind_direction": 225.0,
            "precipitation": 0.0,
            "solar_radiation": 250.0,
        },
    },
    "night_clear_sky": {
        "name": "Night Clear Sky (Max Radiative Cooling)",
        "region": "National",
        "conditions": {
            "temperature": -2.0,
            "humidity": 40.0,
            "wind_speed": 1.0,
            "wind_direction": 0.0,
            "precipitation": 0.0,
            "solar_radiation": 0.0,
        },
    },
}


def get_preset(name: str) -> ClimatePreset | None:
    """Get a climate preset by name."""
    data = CLIMATE_PRESETS.get(name)
    if not data:
        return None
    return ClimatePreset(
        name=data["name"],
        region=data["region"],
        conditions=EnvironmentCondition(**data["conditions"]),
    )


def list_presets() -> list[str]:
    """List all available preset names."""
    return list(CLIMATE_PRESETS.keys())
