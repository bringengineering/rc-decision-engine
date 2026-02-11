"""Spray coverage engine - grid-based coverage analysis.

Combines Navier-Stokes droplet trajectories with road geometry
to compute actual coverage percentage over a discretized grid.
"""

import math
from typing import Any

import numpy as np

from engine.domain.constants import KDS_MIN_BRINE_COVERAGE
from engine.domain.models import EnvironmentCondition, PhysicsAsset
from engine.physics.base import PhysicsEngine
from engine.physics.navier_stokes import NavierStokesEngine


class SprayCoverageEngine(PhysicsEngine):
    """Grid-based spray coverage calculation."""

    def __init__(self, grid_resolution: float = 0.1):
        self.grid_resolution = grid_resolution
        self.ns_engine = NavierStokesEngine()

    def predict(
        self,
        assets: list[PhysicsAsset],
        environment: EnvironmentCondition,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compute grid-based coverage analysis."""
        ns_result = self.ns_engine.predict(assets, environment, params)
        landing_points = ns_result.get("landing_points", [])

        road_segments = [a for a in assets if a.type.value == "road_segment"]
        if not road_segments:
            return {**ns_result, "grid_coverage": 0.0, "grid_size": (0, 0)}

        total_length = sum(r.properties.get("length", 10.0) for r in road_segments)
        total_width = max(r.properties.get("width", 7.0) for r in road_segments)

        nx = max(int(total_length / self.grid_resolution), 1)
        ny = max(int(total_width / self.grid_resolution), 1)
        grid = np.zeros((nx, ny), dtype=bool)

        for pt in landing_points:
            ix = int((pt["x"] + total_length / 2) / self.grid_resolution)
            iy = int((pt["y"] + total_width / 2) / self.grid_resolution)
            splash_cells = max(int(0.05 / self.grid_resolution), 1)
            for dx in range(-splash_cells, splash_cells + 1):
                for dy in range(-splash_cells, splash_cells + 1):
                    gx, gy = ix + dx, iy + dy
                    if 0 <= gx < nx and 0 <= gy < ny:
                        grid[gx, gy] = True

        covered_cells = int(np.sum(grid))
        total_cells = nx * ny
        grid_coverage = covered_cells / total_cells if total_cells > 0 else 0.0

        return {
            **ns_result,
            "grid_coverage": grid_coverage,
            "grid_size": (nx, ny),
            "covered_cells": covered_cells,
            "total_cells": total_cells,
            "coverage_ratio": grid_coverage,
        }

    def compute_safety_factor(
        self,
        prediction: dict[str, Any],
        environment: EnvironmentCondition,
    ) -> float:
        """SF = grid_coverage / required_coverage."""
        coverage = prediction.get("grid_coverage", prediction.get("coverage_ratio", 0.0))
        required = KDS_MIN_BRINE_COVERAGE
        if required <= 0:
            return float("inf")
        return coverage / required
