"""Physics-Informed Neural Network base class.

Architecture: input -> hidden layers (4x64, tanh) -> output
Loss: L_total = L_physics + lambda * L_sensor

The physics loss enforces PDE constraints (Navier-Stokes, heat equation).
The sensor loss matches predictions to real sensor data.
"""

from typing import Any

import torch
import torch.nn as nn


class PINNBase(nn.Module):
    """Base PINN model with physics-informed loss.

    Subclasses implement specific PDE losses (NS, thermal, structural).
    """

    def __init__(
        self,
        input_dim: int = 6,
        output_dim: int = 4,
        hidden_dim: int = 64,
        n_hidden: int = 4,
        activation: str = "tanh",
    ):
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim

        act_fn = nn.Tanh() if activation == "tanh" else nn.ReLU()

        layers = [nn.Linear(input_dim, hidden_dim), act_fn]
        for _ in range(n_hidden - 1):
            layers.extend([nn.Linear(hidden_dim, hidden_dim), act_fn])
        layers.append(nn.Linear(hidden_dim, output_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through the network."""
        return self.network(x)

    def physics_loss(self, x: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        """Compute physics-based loss (PDE residual).

        Must be implemented by subclasses for specific equations.
        """
        raise NotImplementedError

    def sensor_loss(self, y_pred: torch.Tensor, y_sensor: torch.Tensor) -> torch.Tensor:
        """Compute data-fitting loss against sensor measurements."""
        return nn.functional.mse_loss(y_pred, y_sensor)

    def total_loss(
        self,
        x: torch.Tensor,
        y_pred: torch.Tensor,
        y_sensor: torch.Tensor | None = None,
        lambda_sensor: float = 0.1,
    ) -> torch.Tensor:
        """L_total = L_physics + lambda * L_sensor."""
        l_physics = self.physics_loss(x, y_pred)
        if y_sensor is not None:
            l_sensor = self.sensor_loss(y_pred, y_sensor)
            return l_physics + lambda_sensor * l_sensor
        return l_physics

    def freeze_hidden_layers(self):
        """Freeze hidden layers for calibration fine-tuning.

        Only boundary condition parameters remain trainable.
        """
        for name, param in self.named_parameters():
            if "network.0" not in name and f"network.{len(self.network)-1}" not in name:
                param.requires_grad = False

    def unfreeze_all(self):
        """Unfreeze all parameters for full training."""
        for param in self.parameters():
            param.requires_grad = True
