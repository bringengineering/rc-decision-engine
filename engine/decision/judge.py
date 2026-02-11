"""The Judge - Final decision logic for PASS/FAIL/WARNING classification.

Decision Rules:
- FAIL:    Pf >= 20% OR mean SF < 1.0
- WARNING: Mean SF safe, but 95% UCL violates safety target
- PASS:    SF >= 1.5 (safety_factor_target) AND UCL satisfied
"""

from typing import Any

from engine.domain.constants import (
    FAIL_PROBABILITY_THRESHOLD,
    FAIL_SAFETY_FACTOR_THRESHOLD,
    PASS_SAFETY_FACTOR_TARGET,
    MONTE_CARLO_N,
)
from engine.domain.enums import Verdict
from engine.domain.models import (
    DecisionResult,
    EnvironmentCondition,
    PhysicsAsset,
)
from engine.decision.monte_carlo import MonteCarloEngine
from engine.physics.base import PhysicsEngine


class Judge:
    """The Judge - makes PASS/FAIL/WARNING decisions.

    Orchestrates Monte Carlo simulation and applies classification rules.
    """

    def __init__(self, physics_engine: PhysicsEngine, n_samples: int = MONTE_CARLO_N):
        self.mc_engine = MonteCarloEngine(physics_engine, n_samples=n_samples)
        self.n_samples = n_samples

    def decide(
        self,
        assets: list[PhysicsAsset],
        environment: EnvironmentCondition,
        safety_factor_target: float = PASS_SAFETY_FACTOR_TARGET,
        params: dict[str, Any] | None = None,
        seed: int | None = 42,
    ) -> DecisionResult:
        """Run Monte Carlo and classify the result.

        Returns:
            DecisionResult with verdict, failure_probability, safety_factor, etc.
        """
        mc_result = self.mc_engine.run(assets, environment, params, seed=seed)

        pf = mc_result["failure_probability"]
        mean_sf = mc_result["mean_sf"]
        ucl_95 = mc_result["ucl_95"]

        # Classification logic
        if pf >= FAIL_PROBABILITY_THRESHOLD or mean_sf < FAIL_SAFETY_FACTOR_THRESHOLD:
            verdict = Verdict.FAIL
            reasoning = (
                f"FAIL: Failure probability {pf:.1%} "
                f"(threshold: {FAIL_PROBABILITY_THRESHOLD:.0%}), "
                f"Mean SF = {mean_sf:.2f} "
                f"(minimum: {FAIL_SAFETY_FACTOR_THRESHOLD:.1f})"
            )
        elif mean_sf < safety_factor_target or ucl_95 > safety_factor_target * 1.5:
            verdict = Verdict.WARNING
            reasoning = (
                f"WARNING: Mean SF = {mean_sf:.2f} is below target {safety_factor_target:.1f}, "
                f"or 95% UCL = {ucl_95:.2f} indicates tail risk. "
                f"Conditional risk detected."
            )
        else:
            verdict = Verdict.PASS
            reasoning = (
                f"PASS: Mean SF = {mean_sf:.2f} >= target {safety_factor_target:.1f}, "
                f"Failure probability = {pf:.1%} < {FAIL_PROBABILITY_THRESHOLD:.0%}. "
                f"All scenarios within safety limits."
            )

        return DecisionResult(
            verdict=verdict,
            failure_probability=pf,
            mean_safety_factor=mean_sf,
            safety_factor_target=safety_factor_target,
            ucl_95=ucl_95,
            monte_carlo_n=self.n_samples,
            details={
                "std_sf": mc_result["std_sf"],
                "min_sf": mc_result["min_sf"],
                "max_sf": mc_result["max_sf"],
                "percentile_5": mc_result["percentile_5"],
                "percentile_95": mc_result["percentile_95"],
            },
            reasoning=reasoning,
        )
