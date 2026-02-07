"""Simulation API Router — trigger, status, results, WebSocket streaming"""

from uuid import UUID
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth.router import get_current_user
from app.auth.service import decode_access_token, get_user_by_id
from app.models import User, Project, SimulationRun
from app.simulation.service import run_simulation_sync, build_engine_project, build_environment

router = APIRouter(prefix="/api/projects", tags=["simulation"])


class SimulateRequest(BaseModel):
    climate_preset: str = "gangwon_winter_night"


class SimulationStatusResponse(BaseModel):
    id: UUID
    status: str
    climate_preset: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class SimulationResultResponse(BaseModel):
    id: UUID
    status: str
    result: Optional[dict]
    judgment: Optional[dict]
    report_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/{project_id}/simulate", response_model=SimulationResultResponse, status_code=201)
async def trigger_simulation(
    project_id: UUID,
    req: SimulateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """시뮬레이션 실행 (동기 — Phase 1에서는 Celery 없이 직접 실행)"""
    # 프로젝트 로드
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id, Project.owner_id == user.id)
        .options(
            selectinload(Project.road_segments),
            selectinload(Project.spray_devices),
            selectinload(Project.supply_system),
            selectinload(Project.underground_utilities),
        )
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.road_segments:
        raise HTTPException(status_code=400, detail="No road segments defined")
    if not project.spray_devices:
        raise HTTPException(status_code=400, detail="No spray devices defined")

    # 시뮬레이션 실행
    try:
        engine_project = build_engine_project(project)
        env = build_environment(project, req.climate_preset)
        sim_result, judgment, report_text = run_simulation_sync(engine_project, env)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

    # DB에 결과 저장
    run = SimulationRun(
        project_id=project_id,
        triggered_by=user.id,
        climate_preset=req.climate_preset,
        climate_data=env.to_json(),
        status="completed",
        started_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        result=sim_result,
        judgment=judgment,
        report_text=report_text,
    )
    db.add(run)
    project.status = "completed"
    await db.commit()
    await db.refresh(run)

    return run


@router.get("/{project_id}/simulation/latest", response_model=SimulationResultResponse)
async def get_latest_simulation(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SimulationRun)
        .where(SimulationRun.project_id == project_id)
        .order_by(SimulationRun.created_at.desc())
        .limit(1)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="No simulation runs found")
    return run


@router.get("/{project_id}/report")
async def get_report(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SimulationRun)
        .where(SimulationRun.project_id == project_id)
        .order_by(SimulationRun.created_at.desc())
        .limit(1)
    )
    run = result.scalar_one_or_none()
    if not run or not run.report_text:
        raise HTTPException(status_code=404, detail="No report available")
    return {"report": run.report_text, "judgment": run.judgment}


# ─── WebSocket for real-time simulation (Phase 1: simplified) ───

@router.websocket("/ws/projects/{project_id}/simulate")
async def ws_simulate(websocket: WebSocket, project_id: UUID):
    await websocket.accept()
    try:
        # 토큰 인증
        data = await websocket.receive_json()
        token = data.get("token")
        climate_preset = data.get("climate_preset", "gangwon_winter_night")

        if not token:
            await websocket.send_json({"error": "Token required"})
            await websocket.close()
            return

        user_id = decode_access_token(token)
        if not user_id:
            await websocket.send_json({"error": "Invalid token"})
            await websocket.close()
            return

        await websocket.send_json({"status": "authenticated", "message": "Starting simulation..."})

        # DB에서 프로젝트 로드
        async with get_db() as db:
            user = await get_user_by_id(db, user_id)
            result = await db.execute(
                select(Project)
                .where(Project.id == project_id, Project.owner_id == user.id)
                .options(
                    selectinload(Project.road_segments),
                    selectinload(Project.spray_devices),
                    selectinload(Project.supply_system),
                    selectinload(Project.underground_utilities),
                )
            )
            project = result.scalar_one_or_none()

        if not project:
            await websocket.send_json({"error": "Project not found"})
            await websocket.close()
            return

        await websocket.send_json({"status": "loaded", "message": "Project loaded"})

        # 시뮬레이션 실행
        engine_project = build_engine_project(project)
        env = build_environment(project, climate_preset)

        await websocket.send_json({"status": "simulating", "message": "Running simulation..."})
        sim_result, judgment, report_text = run_simulation_sync(engine_project, env)

        await websocket.send_json({
            "status": "completed",
            "result": sim_result,
            "judgment": judgment,
            "report": report_text,
        })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass
