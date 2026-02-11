"""Celery tasks for async simulation execution.

Phase 1: Placeholder - simulation runs synchronously.
Phase 2+: Will dispatch to Celery workers.
"""

from celery import Celery
from app.config import settings

celery_app = Celery(
    "rc_decision",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
)


@celery_app.task(name="simulation.run")
def run_simulation_task(project_id: str, user_id: str, params: dict):
    """Async simulation task (Phase 2+).

    Currently a placeholder. In production, this will:
    1. Load project from DB
    2. Run physics engine
    3. Run Monte Carlo
    4. Store results
    5. Generate report
    """
    # TODO: Implement async execution in Phase 2
    return {"status": "not_implemented", "message": "Use synchronous API for Phase 1"}
