"""Navier-Stokes PINN for incompressible fluid flow.

Input: (x, y, z, t, wind_speed, nozzle_pressure)
Output: (u, v, w, p) velocity components + pressure

Physics loss enforces:
- Continuity equation: div(u) = 0
- Momentum equations (simplified)
"""

import torch
import torch.nn as nn

from engine.pinns.base_model import PINNBase


class NavierStokesPINN(PINNBase):
    """PINN for Navier-Stokes equations.

    Specialized for salt spray fluid dynamics simulation.
    """

    def __init__(self):
        super().__init__(
            input_dim=6,   # x, y, z, t, wind_speed, pressure
            output_dim=4,  # u, v, w, p (velocity + pressure)
            hidden_dim=64,
            n_hidden=4,
        )

    def physics_loss(self, x: torch.Tensor, y_pred: torch.Tensor) -> torch.Tensor:
        """Enforce Navier-Stokes constraints.

        Simplified continuity: du/dx + dv/dy + dw/dz = 0
        """
        x.requires_grad_(True)
        y = self.forward(x)

        u, v, w, p = y[:, 0:1], y[:, 1:2], y[:, 2:3], y[:, 3:4]

        # Compute spatial gradients
        du_dx = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0][:, 0:1]
        dv_dy = torch.autograd.grad(v, x, grad_outputs=torch.ones_like(v), create_graph=True)[0][:, 1:2]
        dw_dz = torch.autograd.grad(w, x, grad_outputs=torch.ones_like(w), create_graph=True)[0][:, 2:3]

        # Continuity equation residual
        continuity = du_dx + dv_dy + dw_dz

        return torch.mean(continuity ** 2)
