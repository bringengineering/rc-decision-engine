"""Tests for physics engines."""

import pytest

from engine.domain.models import EnvironmentCondition, PhysicsAsset
from engine.domain.enums import AssetType
from engine.physics.navier_stokes import NavierStokesEngine
from engine.physics.thermodynamics import ThermodynamicsEngine
from engine.physics.spray_coverage import SprayCoverageEngine


class TestNavierStokesEngine:
    def test_predict_with_devices(self, sample_assets, sample_environment):
        engine = NavierStokesEngine()
        result = engine.predict(sample_assets, sample_environment)
        assert "landing_points" in result
        assert "coverage_ratio" in result
        assert len(result["landing_points"]) > 0

    def test_predict_no_devices(self, sample_road_segment, sample_environment):
        engine = NavierStokesEngine()
        result = engine.predict([sample_road_segment], sample_environment)
        assert result["coverage_ratio"] == 0.0

    def test_safety_factor(self, sample_assets, sample_environment):
        engine = NavierStokesEngine()
        prediction = engine.predict(sample_assets, sample_environment)
        sf = engine.compute_safety_factor(prediction, sample_environment)
        assert sf >= 0.0


class TestThermodynamicsEngine:
    def test_predict_cold(self, sample_assets, sample_environment):
        engine = ThermodynamicsEngine()
        result = engine.predict(sample_assets, sample_environment)
        assert "surface_temperature" in result
        assert "freezing_point" in result
        assert "is_icing" in result

    def test_freezing_point_depression(self):
        engine = ThermodynamicsEngine()
        # 23% NaCl should depress freezing point by ~13.8C
        depression = engine._freezing_point_depression(23.0)
        assert depression < -10.0

    def test_warm_conditions(self, sample_assets):
        engine = ThermodynamicsEngine()
        warm_env = EnvironmentCondition(temperature=10.0, humidity=50.0, wind_speed=2.0, solar_radiation=300.0)
        result = engine.predict(sample_assets, warm_env)
        assert not result["is_icing"]

    def test_safety_factor(self, sample_assets, sample_environment):
        engine = ThermodynamicsEngine()
        prediction = engine.predict(sample_assets, sample_environment)
        sf = engine.compute_safety_factor(prediction, sample_environment)
        assert sf >= 0.0


class TestSprayCoverageEngine:
    def test_grid_coverage(self, sample_assets, sample_environment):
        engine = SprayCoverageEngine(grid_resolution=0.5)
        result = engine.predict(sample_assets, sample_environment)
        assert "grid_coverage" in result
        assert "grid_size" in result
        assert result["grid_coverage"] >= 0.0
        assert result["grid_coverage"] <= 1.0
