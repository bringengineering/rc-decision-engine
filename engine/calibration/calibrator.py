"""Calibrator - adjusts physics parameters based on sensor data.

Phase 1: Simple parameter adjustment.
Phase 2+: PINNs fine-tuning with frozen hidden layers.
"""

from typing import Any

from engine.domain.models import CalibrationResult
from engine.domain.constants import CALIBRATION_LAMBDA


class Calibrator:
    """Reality calibration engine.

    Phase 1 MVP: Adjusts boundary condition parameters proportionally.
    Phase 2+: Fine-tunes PINN boundary layers (freeze hidden, train boundary).
    """

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate

    def calibrate(
        self,
        current_params: dict[str, Any],
        sensor_data: dict[str, Any],
        physics_predictions: dict[str, Any] | None = None,
    ) -> CalibrationResult:
        """Run a calibration cycle.

        Phase 1: Simple proportional correction.
        correction = learning_rate * (sensor_value - predicted_value) / predicted_value

        Args:
            current_params: Current physics boundary parameters.
            sensor_data: Recent sensor measurements.
            physics_predictions: Physics engine predictions for comparison.

        Returns:
            CalibrationResult with corrections applied.
        """
        corrections = {}
        new_params = dict(current_params)
        readings_used = 0

        for param_name, current_value in current_params.items():
            if param_name in sensor_data:
                sensor_value = sensor_data[param_name]
                if current_value != 0:
                    error = (sensor_value - current_value) / abs(current_value)
                    correction = self.learning_rate * error
                    corrections[param_name] = correction
                    new_params[param_name] = current_value * (1.0 + correction)
                    readings_used += 1

        drift_pct = 0.0
        if corrections:
            drift_pct = sum(abs(c) for c in corrections.values()) / len(corrections) * 100

        status = "calibrated" if readings_used > 0 else "insufficient_data"

        return CalibrationResult(
            drift_percentage=drift_pct,
            corrections_applied=corrections,
            new_physics_params=new_params,
            sensor_readings_used=readings_used,
            status=status,
        )
