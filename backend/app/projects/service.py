"""Project Service — CRUD operations"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import (
    Project, RoadSegment, SprayDevice, SupplySystem, UndergroundUtility, User
)
from app.projects import schemas


async def list_projects(db: AsyncSession, user: User) -> List[Project]:
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == user.id)
        .order_by(Project.updated_at.desc())
    )
    return result.scalars().all()


async def get_project(db: AsyncSession, project_id: UUID, user: User) -> Optional[Project]:
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
    return result.scalar_one_or_none()


async def create_project(db: AsyncSession, data: schemas.ProjectCreate, user: User) -> Project:
    project = Project(
        owner_id=user.id,
        org_id=user.org_id,
        name=data.name,
        description=data.description,
        location_name=data.location_name,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def update_project(db: AsyncSession, project: Project, data: schemas.ProjectUpdate) -> Project:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    await db.delete(project)
    await db.commit()


# ─── Road Segments ───

async def add_road_segment(db: AsyncSession, project_id: UUID, data: schemas.RoadSegmentCreate) -> RoadSegment:
    segment = RoadSegment(project_id=project_id, **data.model_dump())
    db.add(segment)
    await db.commit()
    await db.refresh(segment)
    return segment


async def update_road_segment(db: AsyncSession, segment: RoadSegment, data: schemas.RoadSegmentCreate) -> RoadSegment:
    for field, value in data.model_dump().items():
        setattr(segment, field, value)
    await db.commit()
    await db.refresh(segment)
    return segment


# ─── Spray Devices ───

async def add_spray_device(db: AsyncSession, project_id: UUID, data: schemas.SprayDeviceCreate) -> SprayDevice:
    device = SprayDevice(project_id=project_id, **data.model_dump())
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return device


async def update_spray_device(db: AsyncSession, device: SprayDevice, data: schemas.SprayDeviceCreate) -> SprayDevice:
    for field, value in data.model_dump().items():
        setattr(device, field, value)
    await db.commit()
    await db.refresh(device)
    return device


async def delete_spray_device(db: AsyncSession, device: SprayDevice) -> None:
    await db.delete(device)
    await db.commit()


# ─── Supply System ───

async def set_supply_system(db: AsyncSession, project_id: UUID, data: schemas.SupplySystemCreate) -> SupplySystem:
    result = await db.execute(
        select(SupplySystem).where(SupplySystem.project_id == project_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        for field, value in data.model_dump().items():
            setattr(existing, field, value)
        await db.commit()
        await db.refresh(existing)
        return existing

    supply = SupplySystem(project_id=project_id, **data.model_dump())
    db.add(supply)
    await db.commit()
    await db.refresh(supply)
    return supply


# ─── Underground Utilities ───

async def add_utility(db: AsyncSession, project_id: UUID, data: schemas.UndergroundUtilityCreate) -> UndergroundUtility:
    utility = UndergroundUtility(project_id=project_id, **data.model_dump())
    db.add(utility)
    await db.commit()
    await db.refresh(utility)
    return utility
