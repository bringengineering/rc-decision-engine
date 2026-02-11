"""PINN training loop.

Supports:
- Full training from scratch (on simulation data)
- Calibration fine-tuning (freeze hidden layers, tune boundary params)
- Auto-triggered when drift > 5% for > 10 minutes
"""

from typing import Any, Optional

import torch
import torch.optim as optim

from engine.pinns.base_model import PINNBase
from engine.domain.constants import CALIBRATION_LAMBDA


class PINNTrainer:
    """Trains and fine-tunes PINN models."""

    def __init__(
        self,
        model: PINNBase,
        learning_rate: float = 1e-3,
        lambda_sensor: float = CALIBRATION_LAMBDA,
    ):
        self.model = model
        self.learning_rate = learning_rate
        self.lambda_sensor = lambda_sensor
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        self.loss_history: list[float] = []

    def train_step(
        self,
        x_physics: torch.Tensor,
        x_sensor: Optional[torch.Tensor] = None,
        y_sensor: Optional[torch.Tensor] = None,
    ) -> float:
        """Single training step.

        Args:
            x_physics: Collocation points for physics loss.
            x_sensor: Sensor input locations (optional).
            y_sensor: Sensor measurements (optional).

        Returns:
            Total loss value.
        """
        self.optimizer.zero_grad()

        y_pred = self.model(x_physics)
        l_physics = self.model.physics_loss(x_physics, y_pred)

        loss = l_physics
        if x_sensor is not None and y_sensor is not None:
            y_sensor_pred = self.model(x_sensor)
            l_sensor = self.model.sensor_loss(y_sensor_pred, y_sensor)
            loss = l_physics + self.lambda_sensor * l_sensor

        loss.backward()
        self.optimizer.step()

        loss_val = loss.item()
        self.loss_history.append(loss_val)
        return loss_val

    def train(
        self,
        x_physics: torch.Tensor,
        epochs: int = 1000,
        x_sensor: Optional[torch.Tensor] = None,
        y_sensor: Optional[torch.Tensor] = None,
        verbose: bool = False,
    ) -> list[float]:
        """Full training loop.

        Returns:
            List of loss values per epoch.
        """
        self.model.train()
        losses = []

        for epoch in range(epochs):
            loss = self.train_step(x_physics, x_sensor, y_sensor)
            losses.append(loss)
            if verbose and epoch % 100 == 0:
                print(f"Epoch {epoch}: loss = {loss:.6f}")

        return losses

    def calibrate(
        self,
        x_sensor: torch.Tensor,
        y_sensor: torch.Tensor,
        epochs: int = 200,
    ) -> list[float]:
        """Calibration fine-tuning.

        Freezes hidden layers, only tunes input/output layers (boundary conditions).
        """
        self.model.freeze_hidden_layers()
        # Re-create optimizer with only trainable params
        self.optimizer = optim.Adam(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.learning_rate * 0.1,  # Lower LR for fine-tuning
        )

        losses = self.train(
            x_physics=x_sensor,  # Use sensor locations as collocation points
            epochs=epochs,
            x_sensor=x_sensor,
            y_sensor=y_sensor,
        )

        self.model.unfreeze_all()
        return losses

    def save_model(self, path: str):
        """Save model weights."""
        torch.save(self.model.state_dict(), path)

    def load_model(self, path: str):
        """Load model weights."""
        self.model.load_state_dict(torch.load(path, weights_only=True))
