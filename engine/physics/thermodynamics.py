"""Thermodynamics engine for road surface temperature and icing prediction.

Computes heat balance on road surface considering:
- Solar radiation absorption
- Convective heat transfer (wind)
- Radiative cooling (sky)
- Latent heat of freezing/melting
- Brine eutectic depression
"""

import math
from typing import Any

from engine.domain.constants import (
    ASPHALT_THERMAL_CONDUCTIVITY, ASPHALT_SPECIFIC_HEAT, ASPHALT_DENSITY,
    ICE_LATENT_HEAT, STEFAN_BOLTZMANN, NACL_EUTECTIC_TEMP,
    FREEZING_POINT_WATER, ICE_WARNING_TEMP,
)
from engine.domain.models import EnvironmentCondition, PhysicsAsset
from engine.physics.base import PhysicsEngine


class ThermodynamicsEngine(PhysicsEngine):
    """Road surface thermal model for icing prediction."""

    def _convective_heat_transfer_coeff(self, wind_speed: float) -> float:
        """Jurges formula: h = 5.7 + 3.8 * v."""
        return 5.7 + 3.8 * wind_speed

    def _sky_temperature(self, air_temp: float, humidity: float) -> float:
        """Estimate effective sky temperature for radiative cooling."""
        t_air_k = air_temp + 273.15
        emissivity_factor = (0.8 + humidity / 500.0) ** 0.25
        t_sky_k = t_air_k * emissivity_factor
        return t_sky_k - 273.15

    def _freezing_point_depression(self, brine_concentration: float) -> float:
        """Linear approximation: delta_T = -0.6 * concentration (%)."""
        conc = min(brine_concentration, 23.3)
        return -0.6 * conc

    def _compute_surface_temperature(
        self,
        air_temp: float,
        wind_speed: float,
        humidity: float,
        solar_radiation: float,
        surface_emissivity: float = 0.93,
        solar_absorptivity: float = 0.85,
    ) -> float:
        """Steady-state energy balance via Newton iteration."""
        h_conv = self._convective_heat_transfer_coeff(wind_speed)
        t_sky = self._sky_temperature(air_temp, humidity)
        t_sky_k = t_sky + 273.15
        t_air_k = air_temp + 273.15

        t_surface = air_temp

        for _ in range(50):
            t_s_k = t_surface + 273.15
            q_solar = solar_absorptivity * solar_radiation
            q_conv = h_conv * (t_air_k - t_s_k)
            q_rad = surface_emissivity * STEFAN_BOLTZMANN * (t_sky_k**4 - t_s_k**4)
            residual = q_solar + q_conv + q_rad
            dq_conv = -h_conv
            dq_rad = -4.0 * surface_emissivity * STEFAN_BOLTZMANN * t_s_k**3
            derivative = dq_conv + dq_rad
            if abs(derivative) < 1e-12:
                break
            t_surface -= residual / derivative
            if abs(residual) < 0.01:
                break

        return t_surface

    def predict(
        self,
        assets: list[PhysicsAsset],
        environment: EnvironmentCondition,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Predict road surface temperature and icing risk."""
        surface_temp = environment.road_surface_temp
        if surface_temp is None:
            surface_temp = self._compute_surface_temperature(
                air_temp=environment.temperature,
                wind_speed=environment.wind_speed,
                humidity=environment.humidity,
                solar_radiation=environment.solar_radiation,
            )

        if params and "temp_correction" in params:
            surface_temp += params["temp_correction"]

        spray_devices = [a for a in assets if a.type.value == "spray_device"]
        brine_conc = 0.0
        if spray_devices:
            concs = [a.properties.get("brine_concentration", 23.0) for a in spray_devices]
            brine_conc = sum(concs) / len(concs) if concs else 0.0

        freezing_point = FREEZING_POINT_WATER + self._freezing_point_depression(brine_conc)
        is_icing = surface_temp <= freezing_point
        is_warning = surface_temp <= ICE_WARNING_TEMP and not is_icing
        effective_margin = surface_temp - freezing_point

        return {
            "surface_temperature": surface_temp,
            "air_temperature": environment.temperature,
            "freezing_point": freezing_point,
            "freezing_point_depression": self._freezing_point_depression(brine_conc),
            "brine_concentration": brine_conc,
            "is_icing": is_icing,
            "is_warning": is_warning,
            "temperature_margin": effective_margin,
            "convective_coeff": self._convective_heat_transfer_coeff(environment.wind_speed),
        }

    def compute_safety_factor(
        self,
        prediction: dict[str, Any],
        environment: EnvironmentCondition,
    ) -> float:
        """SF = temperature_margin / reference_margin."""
        margin = prediction.get("temperature_margin", 0.0)
        reference_margin = 5.0 / 1.5  # ~3.33C corresponds to SF=1.0
        if reference_margin <= 0:
            return 0.0
        sf = margin / reference_margin
        return max(sf, 0.0)
