"""Abstract base for physics engines."""

from abc import ABC, abstractmethod
from typing import Any

from engine.domain.models import EnvironmentCondition, PhysicsAsset


class PhysicsEngine(ABC):
    """Protocol for all physics engine implementations.

    Each engine takes assets + environment conditions and produces
    physics predictions (velocity fields, temperature fields, coverage, etc.)
    """

    @abstractmethod
    def predict(
        self,
        assets: list[PhysicsAsset],
        environment: EnvironmentCondition,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Run physics prediction.

        Args:
            assets: List of physical assets to simulate.
            environment: Environmental conditions.
            params: Optional calibrated parameters to override defaults.

        Returns:
            Dictionary of prediction results (engine-specific).
        """
        ...

    @abstractmethod
    def compute_safety_factor(
        self,
        prediction: dict[str, Any],
        environment: EnvironmentCondition,
    ) -> float:
        """Compute safety factor from prediction results.

        SF = capacity / demand

        Returns:
            Safety factor (>1.0 means safe, <1.0 means failure).
        """
        ...
