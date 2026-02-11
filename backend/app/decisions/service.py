"""Decision service: manages decision reports."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DecisionReport


async def get_decision(db: AsyncSession, decision_id: UUID) -> DecisionReport | None:
    result = await db.execute(select(DecisionReport).where(DecisionReport.id == decision_id))
    return result.scalar_one_or_none()


async def get_project_decisions(db: AsyncSession, project_id: UUID) -> list[DecisionReport]:
    result = await db.execute(
        select(DecisionReport)
        .where(DecisionReport.project_id == project_id)
        .order_by(DecisionReport.created_at.desc())
    )
    return list(result.scalars().all())
