"""Simulation API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.simulation.schemas import SimulationRequest, SimulationStatusResponse, SimulationResultResponse
from app.simulation import service

router = APIRouter()


@router.post("/{project_id}/simulate", response_model=SimulationStatusResponse)
async def trigger_simulation(
    project_id: UUID,
    data: SimulationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger simulation for a project."""
    try:
        sim_run = await service.run_simulation(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
            simulation_type=data.simulation_type,
            climate_preset=data.climate_preset,
            environment_override=data.environment_override,
            monte_carlo_n=data.monte_carlo_n,
            params_override=data.params_override,
        )
        return SimulationStatusResponse(
            run_id=sim_run.id,
            status=sim_run.status,
            started_at=sim_run.started_at,
            completed_at=sim_run.completed_at,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {e}")


@router.get("/simulation/{run_id}/status", response_model=SimulationStatusResponse)
async def get_simulation_status(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check simulation status."""
    sim_run = await service.get_simulation_run(db, run_id)
    if not sim_run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return SimulationStatusResponse(
        run_id=sim_run.id,
        status=sim_run.status,
        started_at=sim_run.started_at,
        completed_at=sim_run.completed_at,
    )


@router.get("/simulation/{run_id}/result", response_model=SimulationResultResponse)
async def get_simulation_result(
    run_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get simulation results."""
    sim_run = await service.get_simulation_run(db, run_id)
    if not sim_run:
        raise HTTPException(status_code=404, detail="Simulation run not found")
    return sim_run
