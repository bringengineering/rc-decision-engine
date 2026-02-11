"""Simulation orchestration service.

Chains: Physics Engine -> Calibration -> Monte Carlo -> Decision -> Report
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Asset, Project, SimulationRun, DecisionReport
from engine.domain.enums import AssetType, SimulationType
from engine.domain.models import EnvironmentCondition, PhysicsAsset, DecisionResult
from engine.environment.climate import get_preset
from engine.physics.navier_stokes import NavierStokesEngine
from engine.physics.thermodynamics import ThermodynamicsEngine
from engine.physics.spray_coverage import SprayCoverageEngine
from engine.decision.judge import Judge


def _build_physics_assets(db_assets: list[Asset]) -> list[PhysicsAsset]:
    """Convert DB assets to engine domain models."""
    result = []
    for asset in db_assets:
        result.append(PhysicsAsset(
            id=str(asset.id),
            type=AssetType(asset.type),
            name=asset.name,
            geometry=asset.geometry_json,
            properties=asset.properties or {},
        ))
    return result


def _resolve_environment(
    climate_preset: str | None, environment_override: dict | None
) -> EnvironmentCondition:
    """Build environment from preset or override."""
    if climate_preset:
        preset = get_preset(climate_preset)
        if preset:
            env = preset.conditions
            if environment_override:
                data = env.model_dump()
                data.update(environment_override)
                return EnvironmentCondition(**data)
            return env

    if environment_override:
        return EnvironmentCondition(**environment_override)

    return EnvironmentCondition()  # defaults


def _get_physics_engine(sim_type: str):
    """Select the appropriate physics engine."""
    if sim_type == "thermal":
        return ThermodynamicsEngine()
    elif sim_type == "fluid":
        return NavierStokesEngine()
    else:  # salt_spray (default) uses grid coverage
        return SprayCoverageEngine()


async def run_simulation(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
    simulation_type: str = "salt_spray",
    climate_preset: str | None = None,
    environment_override: dict | None = None,
    monte_carlo_n: int = 1000,
    params_override: dict | None = None,
) -> SimulationRun:
    """Execute simulation pipeline synchronously (Phase 1).

    In Phase 2+, this will be dispatched to Celery.
    """
    # Load project with assets
    result = await db.execute(
        select(Project).options(selectinload(Project.assets)).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise ValueError(f"Project {project_id} not found")

    # Create simulation run record
    sim_run = SimulationRun(
        project_id=project_id,
        triggered_by=user_id,
        simulation_type=simulation_type,
        input_params={
            "climate_preset": climate_preset,
            "environment_override": environment_override,
            "monte_carlo_n": monte_carlo_n,
        },
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(sim_run)
    await db.flush()

    try:
        # Build inputs
        physics_assets = _build_physics_assets(project.assets)
        environment = _resolve_environment(climate_preset, environment_override)
        physics_engine = _get_physics_engine(simulation_type)

        # Run The Judge (includes Monte Carlo)
        judge = Judge(physics_engine, n_samples=monte_carlo_n)
        decision: DecisionResult = judge.decide(
            assets=physics_assets,
            environment=environment,
            safety_factor_target=project.safety_factor_target,
            params=params_override,
        )

        # Store results
        sim_run.result = {
            "verdict": decision.verdict.value,
            "failure_probability": decision.failure_probability,
            "mean_safety_factor": decision.mean_safety_factor,
            "ucl_95": decision.ucl_95,
            "reasoning": decision.reasoning,
            "details": decision.details,
        }
        sim_run.status = "completed"
        sim_run.completed_at = datetime.now(timezone.utc)

        # Create decision report
        report = DecisionReport(
            project_id=project_id,
            simulation_run_id=sim_run.id,
            status=decision.verdict.value,
            failure_probability=decision.failure_probability,
            safety_factor_result=decision.mean_safety_factor,
            safety_factor_target=decision.safety_factor_target,
            monte_carlo_n=decision.monte_carlo_n,
            ucl_95=decision.ucl_95,
            details=decision.details,
        )
        db.add(report)
        await db.flush()

    except Exception as e:
        sim_run.status = "failed"
        sim_run.result = {"error": str(e)}
        sim_run.completed_at = datetime.now(timezone.utc)
        await db.flush()

    return sim_run


async def get_simulation_run(db: AsyncSession, run_id: UUID) -> SimulationRun | None:
    result = await db.execute(select(SimulationRun).where(SimulationRun.id == run_id))
    return result.scalar_one_or_none()
