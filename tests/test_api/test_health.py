"""Tests for health check endpoint."""

import pytest


class TestHealthEndpoint:
    """Basic tests that don't require database."""

    def test_verdict_values(self):
        from engine.domain.enums import Verdict
        assert Verdict.PASS == "PASS"
        assert Verdict.FAIL == "FAIL"
        assert Verdict.WARNING == "WARNING"

    def test_climate_presets_exist(self):
        from engine.environment.climate import CLIMATE_PRESETS, list_presets
        assert len(CLIMATE_PRESETS) > 0
        assert "gangwon_winter_severe" in CLIMATE_PRESETS
        names = list_presets()
        assert len(names) == len(CLIMATE_PRESETS)
