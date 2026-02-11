"""Simplified Navier-Stokes fluid dynamics engine for salt spray simulation.

Phase 1 MVP: Parametric model for spray droplet trajectories under wind.
Uses simplified ballistic trajectory with drag forces.
"""

import math
from typing import Any

import numpy as np

from engine.domain.constants import (
    AIR_DENSITY, BRINE_DENSITY_23PCT, DROPLET_DRAG_COEFF, GRAVITY,
    SPRAY_VELOCITY_COEFF, KDS_MIN_BRINE_COVERAGE,
)
from engine.domain.models import EnvironmentCondition, PhysicsAsset, SprayDeviceParams
from engine.physics.base import PhysicsEngine


class NavierStokesEngine(PhysicsEngine):
    """Simplified NS-based spray dynamics.

    Models droplet trajectories considering:
    - Initial spray velocity from nozzle pressure
    - Gravitational settling
    - Aerodynamic drag
    - Wind drift
    - Droplet size distribution (Rosin-Rammler)
    """

    def _compute_spray_velocity(self, pressure: float, density: float) -> float:
        """Bernoulli equation: v = Cv * sqrt(2 * P / rho)."""
        return SPRAY_VELOCITY_COEFF * math.sqrt(2.0 * pressure / density)

    def _droplet_trajectory(
        self,
        v0: float,
        angle_rad: float,
        height: float,
        wind_speed: float,
        wind_angle_rad: float,
        droplet_diameter: float,
    ) -> tuple[float, float]:
        """Compute landing position (x, y) of a single droplet.

        Uses Euler integration for trajectory with drag forces.
        Returns (distance_along_spray, lateral_drift).
        """
        dt = 0.001  # Time step (s)
        max_time = 5.0  # Max simulation time

        # Initial conditions
        vx = v0 * math.cos(angle_rad)
        vy = 0.0
        vz = v0 * math.sin(angle_rad)
        x, y, z = 0.0, 0.0, height

        # Droplet properties
        mass = (math.pi / 6.0) * droplet_diameter**3 * BRINE_DENSITY_23PCT
        area = (math.pi / 4.0) * droplet_diameter**2

        # Wind components
        wx = wind_speed * math.cos(wind_angle_rad)
        wy = wind_speed * math.sin(wind_angle_rad)

        t = 0.0
        while t < max_time and z > 0:
            # Relative velocity (droplet - air/wind)
            rel_vx = vx - wx
            rel_vy = vy - wy
            rel_vz = vz
            rel_speed = math.sqrt(rel_vx**2 + rel_vy**2 + rel_vz**2)

            if rel_speed > 0:
                drag = 0.5 * AIR_DENSITY * DROPLET_DRAG_COEFF * area * rel_speed
                ax = -drag * rel_vx / (mass * rel_speed)
                ay = -drag * rel_vy / (mass * rel_speed)
                az = -GRAVITY - drag * rel_vz / (mass * rel_speed)
            else:
                ax, ay, az = 0.0, 0.0, -GRAVITY

            vx += ax * dt
            vy += ay * dt
            vz += az * dt
            x += vx * dt
            y += vy * dt
            z += vz * dt
            t += dt

        return x, y

    def predict(
        self,
        assets: list[PhysicsAsset],
        environment: EnvironmentCondition,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Predict spray coverage pattern for all spray devices."""
        spray_devices = [a for a in assets if a.type.value == "spray_device"]
        road_segments = [a for a in assets if a.type.value == "road_segment"]

        if not spray_devices:
            return {"landing_points": [], "coverage_ratio": 0.0, "total_coverage_area": 0.0}

        # Compute total road area
        total_road_area = 0.0
        for road in road_segments:
            rp = road.properties
            total_road_area += rp.get("length", 10.0) * rp.get("width", 7.0)

        all_landing_points = []
        wind_angle_rad = math.radians(environment.wind_direction)

        for device in spray_devices:
            dp = device.properties
            spray_params = SprayDeviceParams(**dp) if dp else SprayDeviceParams()

            v0 = self._compute_spray_velocity(spray_params.pump_pressure, BRINE_DENSITY_23PCT)
            half_angle = math.radians(spray_params.spray_angle / 2.0)
            orientation_rad = math.radians(spray_params.orientation)

            # Generate droplet samples across spray cone
            n_droplets = 50
            droplet_sizes = np.random.lognormal(
                mean=np.log(spray_params.nozzle_diameter * 0.3),
                sigma=0.3,
                size=n_droplets,
            )

            for i in range(n_droplets):
                angle_offset = -half_angle + 2 * half_angle * (i / max(n_droplets - 1, 1))
                spray_angle = orientation_rad + angle_offset
                x, y = self._droplet_trajectory(
                    v0=v0,
                    angle_rad=math.radians(30),
                    height=spray_params.mounting_height,
                    wind_speed=environment.wind_speed,
                    wind_angle_rad=wind_angle_rad,
                    droplet_diameter=float(droplet_sizes[i]),
                )
                cos_a, sin_a = math.cos(spray_angle), math.sin(spray_angle)
                landing_x = x * cos_a - y * sin_a
                landing_y = x * sin_a + y * cos_a
                all_landing_points.append({"x": landing_x, "y": landing_y})

        # Estimate coverage area
        if all_landing_points:
            xs = [p["x"] for p in all_landing_points]
            ys = [p["y"] for p in all_landing_points]
            coverage_width = max(xs) - min(xs)
            coverage_length = max(ys) - min(ys)
            coverage_area = coverage_width * coverage_length * 0.7
        else:
            coverage_area = 0.0

        coverage_ratio = min(coverage_area / total_road_area, 1.0) if total_road_area > 0 else 0.0

        # Apply calibration corrections
        if params and "coverage_correction" in params:
            coverage_ratio *= (1.0 + params["coverage_correction"])
            coverage_ratio = min(max(coverage_ratio, 0.0), 1.0)

        return {
            "landing_points": all_landing_points,
            "coverage_ratio": coverage_ratio,
            "total_coverage_area": coverage_area,
            "total_road_area": total_road_area,
            "spray_velocity": v0 if spray_devices else 0.0,
            "wind_effect": {
                "speed": environment.wind_speed,
                "direction": environment.wind_direction,
            },
        }

    def compute_safety_factor(
        self,
        prediction: dict[str, Any],
        environment: EnvironmentCondition,
    ) -> float:
        """SF = actual_coverage / required_coverage."""
        coverage_ratio = prediction.get("coverage_ratio", 0.0)
        required = KDS_MIN_BRINE_COVERAGE
        if required <= 0:
            return float("inf")
        return coverage_ratio / required
