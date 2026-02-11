"""Optimized PINN inference (no gradients, batched prediction)."""

from typing import Any

import torch
import numpy as np

from engine.pinns.base_model import PINNBase


class PINNInference:
    """Fast inference engine for trained PINN models.

    Runs predictions without gradient computation for speed.
    """

    def __init__(self, model: PINNBase):
        self.model = model
        self.model.eval()

    @torch.no_grad()
    def predict(self, inputs: np.ndarray) -> np.ndarray:
        """Run batched inference.

        Args:
            inputs: NumPy array of shape (N, input_dim).

        Returns:
            NumPy array of shape (N, output_dim).
        """
        x = torch.tensor(inputs, dtype=torch.float32)
        y = self.model(x)
        return y.numpy()

    @torch.no_grad()
    def predict_single(self, **kwargs) -> dict[str, float]:
        """Predict for a single point with named parameters.

        Example:
            result = inference.predict_single(x=1.0, y=2.0, z=0.0, t=0.0, wind=5.0, pressure=3e5)
        """
        values = list(kwargs.values())
        x = torch.tensor([values], dtype=torch.float32)
        y = self.model(x)
        output = y[0].numpy()

        # Map to named outputs based on model type
        if self.model.output_dim == 4:
            return {"u": float(output[0]), "v": float(output[1]), "w": float(output[2]), "p": float(output[3])}
        elif self.model.output_dim == 1:
            return {"temperature": float(output[0])}
        else:
            return {f"output_{i}": float(output[i]) for i in range(len(output))}

    @classmethod
    def from_checkpoint(cls, model_class: type, checkpoint_path: str) -> "PINNInference":
        """Load a trained model from checkpoint."""
        model = model_class()
        model.load_state_dict(torch.load(checkpoint_path, weights_only=True))
        return cls(model)
