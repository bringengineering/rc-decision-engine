"""Tests for Monte Carlo engine and decision logic."""

import pytest

from engine.domain.models import EnvironmentCondition
from engine.domain.enums import Verdict
from engine.physics.spray_coverage import SprayCoverageEngine
from engine.decision.monte_carlo import MonteCarloEngine
from engine.decision.judge import Judge


class TestMonteCarloEngine:
    def test_run_returns_statistics(self, sample_assets, sample_environment):
        engine = SprayCoverageEngine(grid_resolution=1.0)
        mc = MonteCarloEngine(engine, n_samples=50)
        result = mc.run(sample_assets, sample_environment, seed=42)
        assert "mean_sf" in result
        assert "failure_probability" in result
        assert "ucl_95" in result
        assert result["n_samples"] == 50
        assert len(result["safety_factors"]) == 50

    def test_reproducible_with_seed(self, sample_assets, sample_environment):
        engine = SprayCoverageEngine(grid_resolution=1.0)
        mc = MonteCarloEngine(engine, n_samples=20)
        r1 = mc.run(sample_assets, sample_environment, seed=42)
        r2 = mc.run(sample_assets, sample_environment, seed=42)
        assert r1["mean_sf"] == r2["mean_sf"]


class TestJudge:
    def test_decide_returns_verdict(self, sample_assets, sample_environment):
        engine = SprayCoverageEngine(grid_resolution=1.0)
        judge = Judge(engine, n_samples=50)
        decision = judge.decide(sample_assets, sample_environment, seed=42)
        assert decision.verdict in (Verdict.PASS, Verdict.WARNING, Verdict.FAIL)
        assert 0.0 <= decision.failure_probability <= 1.0
        assert decision.mean_safety_factor >= 0.0
        assert decision.reasoning != ""

    def test_high_wind_increases_failure(self, sample_assets):
        engine = SprayCoverageEngine(grid_resolution=1.0)
        judge = Judge(engine, n_samples=50)

        calm = EnvironmentCondition(temperature=-5.0, wind_speed=1.0, humidity=70.0)
        windy = EnvironmentCondition(temperature=-5.0, wind_speed=15.0, humidity=70.0)

        decision_calm = judge.decide(sample_assets, calm, seed=42)
        decision_windy = judge.decide(sample_assets, windy, seed=42)

        # Windy conditions should have higher failure probability
        assert decision_windy.failure_probability >= decision_calm.failure_probability
