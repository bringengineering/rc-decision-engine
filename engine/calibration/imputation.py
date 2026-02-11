"""Physics-based data imputation for missing sensor values.

When sensor data has NaN gaps, uses the physics model to impute
missing values rather than simple interpolation/average.
"""

from typing import Any, Optional

import numpy as np


class PhysicsImputer:
    """Imputes missing sensor data using physics models.

    Instead of simple average/interpolation, uses the physics engine
    to predict what the sensor *should* read given surrounding conditions.
    """

    def __init__(self, physics_engine=None):
        self.physics_engine = physics_engine

    def impute(
        self,
        sensor_data: list[dict],
        environment: Any = None,
        assets: list = None,
    ) -> list[dict]:
        """Fill NaN values in sensor data using physics predictions.

        Args:
            sensor_data: List of {"time": str, "value": float|None} entries.
            environment: Current environment conditions.
            assets: Physical assets for context.

        Returns:
            List with NaN values replaced by physics-based estimates.
        """
        if not sensor_data:
            return sensor_data

        result = []
        values = [d.get("value") for d in sensor_data]
        valid_values = [v for v in values if v is not None and not (isinstance(v, float) and np.isnan(v))]

        for entry in sensor_data:
            new_entry = dict(entry)
            value = entry.get("value")

            if value is None or (isinstance(value, float) and np.isnan(value)):
                # Phase 1: Use physics engine if available, else weighted neighbor average
                if self.physics_engine and environment and assets:
                    try:
                        prediction = self.physics_engine.predict(assets, environment)
                        # Use the predicted value as imputation
                        new_entry["value"] = prediction.get("surface_temperature", np.mean(valid_values) if valid_values else 0.0)
                        new_entry["imputed"] = True
                        new_entry["method"] = "physics"
                    except Exception:
                        new_entry["value"] = float(np.mean(valid_values)) if valid_values else 0.0
                        new_entry["imputed"] = True
                        new_entry["method"] = "fallback_mean"
                else:
                    new_entry["value"] = float(np.mean(valid_values)) if valid_values else 0.0
                    new_entry["imputed"] = True
                    new_entry["method"] = "mean"
            else:
                new_entry["imputed"] = False

            result.append(new_entry)

        return result
