"""Project CRUD service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Project


async def create_project(db: AsyncSession, owner_id: UUID, **kwargs) -> Project:
    project = Project(owner_id=owner_id, **kwargs)
    db.add(project)
    await db.flush()
    return project


async def get_projects(db: AsyncSession, owner_id: UUID) -> list[Project]:
    result = await db.execute(
        select(Project).where(Project.owner_id == owner_id).order_by(Project.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, project_id: UUID, owner_id: UUID) -> Project | None:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.assets))
        .where(Project.id == project_id, Project.owner_id == owner_id)
    )
    return result.scalar_one_or_none()


async def update_project(db: AsyncSession, project: Project, **kwargs) -> Project:
    for key, value in kwargs.items():
        if value is not None:
            setattr(project, key, value)
    await db.flush()
    return project


async def delete_project(db: AsyncSession, project: Project):
    await db.delete(project)
    await db.flush()
