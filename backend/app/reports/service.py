"""Report generation orchestration service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DecisionReport, Project
from app.reports.pdf_generator import generate_pdf
from app.db.minio_client import minio_manager


async def generate_report(db: AsyncSession, project_id: UUID, decision_id: UUID | None = None) -> DecisionReport:
    """Generate a PDF report for a decision.

    Assembles data, renders PDF, uploads to MinIO, and updates the decision record.
    """
    # Get the decision report
    if decision_id:
        result = await db.execute(select(DecisionReport).where(DecisionReport.id == decision_id))
        decision = result.scalar_one_or_none()
    else:
        # Get latest decision for the project
        result = await db.execute(
            select(DecisionReport)
            .where(DecisionReport.project_id == project_id)
            .order_by(DecisionReport.created_at.desc())
            .limit(1)
        )
        decision = result.scalar_one_or_none()

    if not decision:
        raise ValueError("No decision report found")

    # Get project info
    proj_result = await db.execute(select(Project).where(Project.id == project_id))
    project = proj_result.scalar_one_or_none()

    # Generate PDF
    report_data = {
        "project_name": project.name if project else "Unknown",
        "project_location": project.location_name if project else "",
        "verdict": decision.status,
        "failure_probability": decision.failure_probability,
        "safety_factor_result": decision.safety_factor_result,
        "safety_factor_target": decision.safety_factor_target,
        "monte_carlo_n": decision.monte_carlo_n,
        "ucl_95": decision.ucl_95,
        "details": decision.details or {},
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    pdf_bytes = generate_pdf(report_data)

    # Upload to MinIO
    object_name = f"reports/{project_id}/{decision.id}.pdf"
    try:
        pdf_url = minio_manager.upload_pdf(object_name, pdf_bytes)
        decision.pdf_url = pdf_url
        await db.flush()
    except Exception:
        # If MinIO is unavailable, still return the decision
        pass

    return decision


async def get_report_pdf(db: AsyncSession, decision_id: UUID) -> bytes | None:
    """Download a report PDF from MinIO."""
    result = await db.execute(select(DecisionReport).where(DecisionReport.id == decision_id))
    decision = result.scalar_one_or_none()
    if not decision or not decision.pdf_url:
        return None
    try:
        object_name = decision.pdf_url.lstrip("/").split("/", 1)[-1]
        return minio_manager.get_file(object_name)
    except Exception:
        return None
