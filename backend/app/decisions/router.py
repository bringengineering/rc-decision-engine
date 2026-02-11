"""Decision API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.decisions.schemas import DecisionResponse
from app.decisions import service

router = APIRouter()


@router.get("/decisions/{decision_id}", response_model=DecisionResponse)
async def get_decision(
    decision_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a decision report by ID."""
    decision = await service.get_decision(db, decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision report not found")
    return decision


@router.get("/projects/{project_id}/decisions", response_model=list[DecisionResponse])
async def get_project_decisions(
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all decision reports for a project."""
    return await service.get_project_decisions(db, project_id)
