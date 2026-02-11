"""Asset CRUD service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Asset


async def create_asset(db: AsyncSession, project_id: UUID, **kwargs) -> Asset:
    asset = Asset(project_id=project_id, **kwargs)
    db.add(asset)
    await db.flush()
    return asset


async def bulk_create_assets(db: AsyncSession, project_id: UUID, assets_data: list[dict]) -> list[Asset]:
    assets = [Asset(project_id=project_id, **data) for data in assets_data]
    db.add_all(assets)
    await db.flush()
    return assets


async def get_assets(db: AsyncSession, project_id: UUID) -> list[Asset]:
    result = await db.execute(
        select(Asset).where(Asset.project_id == project_id).order_by(Asset.created_at)
    )
    return list(result.scalars().all())


async def get_asset(db: AsyncSession, asset_id: UUID) -> Asset | None:
    result = await db.execute(select(Asset).where(Asset.id == asset_id))
    return result.scalar_one_or_none()


async def update_asset(db: AsyncSession, asset: Asset, **kwargs) -> Asset:
    for key, value in kwargs.items():
        if value is not None:
            setattr(asset, key, value)
    await db.flush()
    return asset


async def delete_asset(db: AsyncSession, asset: Asset):
    await db.delete(asset)
    await db.flush()
