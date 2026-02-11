"""Reports API endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.db.models import User
from app.dependencies import get_current_user
from app.reports.schemas import ReportGenerateRequest, ReportResponse
from app.reports import service

router = APIRouter()


@router.post("/generate/{project_id}", response_model=ReportResponse)
async def generate_report(
    project_id: UUID,
    data: ReportGenerateRequest | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a PDF report for a project."""
    try:
        decision_id = data.decision_id if data else None
        report = await service.generate_report(db, project_id, decision_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{decision_id}/pdf")
async def download_pdf(
    decision_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a report PDF."""
    pdf_bytes = await service.get_report_pdf(db, decision_id)
    if not pdf_bytes:
        raise HTTPException(status_code=404, detail="Report PDF not found")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{decision_id}.pdf"},
    )
