"""Projects API Router — Full CRUD"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.router import get_current_user
from app.models import User
from app.projects import schemas, service

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[schemas.ProjectListItem])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.list_projects(db, user)


@router.post("", response_model=schemas.ProjectResponse, status_code=201)
async def create_project(
    data: schemas.ProjectCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.create_project(db, data, user)


@router.get("/{project_id}", response_model=schemas.ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=schemas.ProjectResponse)
async def update_project(
    project_id: UUID,
    data: schemas.ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await service.update_project(db, project, data)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await service.delete_project(db, project)


# ─── Road Segments ───

@router.post("/{project_id}/roads", response_model=schemas.RoadSegmentResponse, status_code=201)
async def add_road(
    project_id: UUID,
    data: schemas.RoadSegmentCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await service.add_road_segment(db, project_id, data)


# ─── Spray Devices ───

@router.post("/{project_id}/devices", response_model=schemas.SprayDeviceResponse, status_code=201)
async def add_device(
    project_id: UUID,
    data: schemas.SprayDeviceCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await service.add_spray_device(db, project_id, data)


@router.delete("/{project_id}/devices/{device_db_id}", status_code=204)
async def remove_device(
    project_id: UUID,
    device_db_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models import SprayDevice
    result = await db.execute(
        select(SprayDevice).where(SprayDevice.id == device_db_id, SprayDevice.project_id == project_id)
    )
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    await service.delete_spray_device(db, device)


# ─── Supply System ───

@router.put("/{project_id}/supply", response_model=schemas.SupplySystemResponse)
async def set_supply(
    project_id: UUID,
    data: schemas.SupplySystemCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await service.set_supply_system(db, project_id, data)


# ─── Underground Utilities ───

@router.post("/{project_id}/utilities", response_model=schemas.UndergroundUtilityResponse, status_code=201)
async def add_utility(
    project_id: UUID,
    data: schemas.UndergroundUtilityCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = await service.get_project(db, project_id, user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await service.add_utility(db, project_id, data)
