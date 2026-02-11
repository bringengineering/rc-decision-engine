"""Drift detector - monitors physics vs sensor divergence.

When drift exceeds 5% for more than 10 minutes,
triggers re-calibration of boundary condition parameters.
"""

from typing import Any

from engine.domain.constants import DRIFT_THRESHOLD_PCT, DRIFT_SUSTAINED_MINUTES


class DriftDetector:
    """Monitors the gap between physics predictions and sensor readings."""

    def __init__(
        self,
        threshold_pct: float = DRIFT_THRESHOLD_PCT,
        sustained_minutes: int = DRIFT_SUSTAINED_MINUTES,
    ):
        self.threshold_pct = threshold_pct
        self.sustained_minutes = sustained_minutes

    def compute_drift(
        self,
        physics_params: dict[str, Any],
        sensor_data: dict[str, Any],
    ) -> float:
        """Compute drift percentage between physics prediction and sensor reality.

        Phase 1 MVP: Simple parameter comparison.
        Phase 2+: Will use InfluxDB sensor streams and PINN predictions.

        Returns:
            Drift percentage (0-100).
        """
        if not sensor_data or not physics_params:
            return 0.0

        total_drift = 0.0
        count = 0
        for param_name, predicted_value in physics_params.items():
            if param_name in sensor_data and predicted_value != 0:
                actual_value = sensor_data[param_name]
                drift = abs(actual_value - predicted_value) / abs(predicted_value) * 100
                total_drift += drift
                count += 1

        return total_drift / count if count > 0 else 0.0

    def should_recalibrate(self, drift_history: list[dict]) -> bool:
        """Check if drift has exceeded threshold for sustained period.

        Args:
            drift_history: List of {"drift_pct": float, "at": str} entries.

        Returns:
            True if recalibration should be triggered.
        """
        if not drift_history:
            return False

        # Check last N entries (where N approximates sustained_minutes)
        recent = drift_history[-self.sustained_minutes:]
        if len(recent) < self.sustained_minutes:
            return False

        return all(entry.get("drift_pct", 0) > self.threshold_pct for entry in recent)
