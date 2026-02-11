"""Tests for The Judge decision logic."""

import pytest

from engine.domain.enums import Verdict
from engine.domain.constants import FAIL_PROBABILITY_THRESHOLD


class TestVerdictClassification:
    """Test the classification rules directly."""

    def test_fail_high_probability(self):
        """Pf >= 20% should result in FAIL."""
        assert FAIL_PROBABILITY_THRESHOLD == 0.20

    def test_verdict_enum(self):
        assert Verdict.PASS.value == "PASS"
        assert Verdict.FAIL.value == "FAIL"
        assert Verdict.WARNING.value == "WARNING"
