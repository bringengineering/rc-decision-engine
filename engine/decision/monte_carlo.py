"""Monte Carlo sampling engine for probabilistic risk assessment.

Generates N=1000 scenarios by sampling from input parameter distributions
and runs physics predictions for each to compute safety factor distribution.
"""

from typing import Any

import numpy as np

from engine.domain.constants import MONTE_CARLO_N
from engine.domain.models import EnvironmentCondition, PhysicsAsset
from engine.physics.base import PhysicsEngine


class MonteCarloEngine:
    """Monte Carlo risk assessment engine.

    Samples N scenarios from environmental parameter distributions
    and computes safety factor statistics.
    """

    def __init__(self, physics_engine: PhysicsEngine, n_samples: int = MONTE_CARLO_N):
        self.physics_engine = physics_engine
        self.n_samples = n_samples

    def _sample_environment(
        self, base: EnvironmentCondition, seed: int | None = None
    ) -> list[EnvironmentCondition]:
        """Generate N sampled environments with uncertainty.

        Applies Gaussian noise to key parameters:
        - Temperature: std = 2.0 C
        - Wind speed: std = 1.5 m/s (clipped >= 0)
        - Humidity: std = 10% (clipped 0-100)
        - Wind direction: std = 15 degrees
        """
        rng = np.random.default_rng(seed)
        samples = []
        for _ in range(self.n_samples):
            samples.append(EnvironmentCondition(
                temperature=float(rng.normal(base.temperature, 2.0)),
                humidity=float(np.clip(rng.normal(base.humidity, 10.0), 0, 100)),
                wind_speed=float(max(0, rng.normal(base.wind_speed, 1.5))),
                wind_direction=float(rng.normal(base.wind_direction, 15.0) % 360),
                precipitation=float(max(0, rng.normal(base.precipitation, 0.5))),
                solar_radiation=float(max(0, rng.normal(base.solar_radiation, 50.0))),
                road_surface_temp=base.road_surface_temp,
            ))
        return samples

    def run(
        self,
        assets: list[PhysicsAsset],
        environment: EnvironmentCondition,
        params: dict[str, Any] | None = None,
        seed: int | None = 42,
    ) -> dict[str, Any]:
        """Run Monte Carlo simulation.

        Returns:
            Dictionary with safety_factors, mean_sf, std_sf, pf, ucl_95, etc.
        """
        sampled_envs = self._sample_environment(environment, seed=seed)
        safety_factors = []

        for env in sampled_envs:
            try:
                prediction = self.physics_engine.predict(assets, env, params)
                sf = self.physics_engine.compute_safety_factor(prediction, env)
                safety_factors.append(sf)
            except Exception:
                safety_factors.append(0.0)

        sf_array = np.array(safety_factors)
        mean_sf = float(np.mean(sf_array))
        std_sf = float(np.std(sf_array))
        pf = float(np.mean(sf_array < 1.0))  # Probability of failure

        # 95% Upper Confidence Limit
        ucl_95 = float(mean_sf + 1.96 * std_sf)

        return {
            "safety_factors": safety_factors,
            "mean_sf": mean_sf,
            "std_sf": std_sf,
            "failure_probability": pf,
            "ucl_95": ucl_95,
            "n_samples": self.n_samples,
            "min_sf": float(np.min(sf_array)),
            "max_sf": float(np.max(sf_array)),
            "percentile_5": float(np.percentile(sf_array, 5)),
            "percentile_95": float(np.percentile(sf_array, 95)),
        }
