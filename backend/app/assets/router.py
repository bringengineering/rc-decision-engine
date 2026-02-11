"""Asset API endpoints — nested under /api/projects/{project_id}/assets."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.assets.schemas import AssetCreate, AssetUpdate, AssetResponse, AssetBulkCreate
from app.assets import service

router = APIRouter()


@router.get("/{project_id}/assets", response_model=list[AssetResponse])
async def list_assets(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_assets(db, project_id)


@router.post("/{project_id}/assets", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    project_id: UUID,
    data: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.create_asset(db, project_id, **data.model_dump())


@router.post("/{project_id}/assets/bulk", response_model=list[AssetResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_assets(
    project_id: UUID,
    data: AssetBulkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Bulk import assets from Revit."""
    assets_data = [a.model_dump() for a in data.assets]
    return await service.bulk_create_assets(db, project_id, assets_data)


@router.get("/{project_id}/assets/{asset_id}", response_model=AssetResponse)
async def get_asset(
    project_id: UUID,
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{project_id}/assets/{asset_id}", response_model=AssetResponse)
async def update_asset(
    project_id: UUID,
    asset_id: UUID,
    data: AssetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    return await service.update_asset(db, asset, **data.model_dump(exclude_unset=True))


@router.delete("/{project_id}/assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    project_id: UUID,
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    asset = await service.get_asset(db, asset_id)
    if not asset or asset.project_id != project_id:
        raise HTTPException(status_code=404, detail="Asset not found")
    await service.delete_asset(db, asset)
