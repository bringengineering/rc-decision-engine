"""Thermal PINN for heat equation.

Input: (x, y, t, T_air, solar_radiation, wind_speed)
Output: T_surface (road surface temperature field)

Physics loss enforces energy conservation.
"""

import torch

from engine.pinns.base_model import PINNBase


class ThermalPINN(PINNBase):
    """PINN for heat equation on road surface."""

    def __init__(self):
        super().__init__(
            input_dim=6,   # x, y, t, T_air, solar, wind
            output_dim=1,  # T_surface
            hidden_dim=64,
            n_hidden=4,
        )

    def physics_loss(self, x: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        """Enforce heat equation: dT/dt = alpha * laplacian(T) + source.

        Simplified: penalize large spatial temperature gradients
        and temporal discontinuities.
        """
        x.requires_grad_(True)
        T = self.forward(x)

        # Compute gradients
        grads = torch.autograd.grad(T, x, grad_outputs=torch.ones_like(T), create_graph=True)[0]
        dT_dx = grads[:, 0:1]
        dT_dy = grads[:, 1:2]
        dT_dt = grads[:, 2:3]

        # Second derivatives (Laplacian)
        d2T_dx2 = torch.autograd.grad(dT_dx, x, grad_outputs=torch.ones_like(dT_dx), create_graph=True)[0][:, 0:1]
        d2T_dy2 = torch.autograd.grad(dT_dy, x, grad_outputs=torch.ones_like(dT_dy), create_graph=True)[0][:, 1:2]

        # Thermal diffusivity of asphalt
        alpha = 3.47e-7  # m^2/s

        # Heat equation residual: dT/dt - alpha * (d2T/dx2 + d2T/dy2) = source
        laplacian = d2T_dx2 + d2T_dy2
        residual = dT_dt - alpha * laplacian

        return torch.mean(residual ** 2)
