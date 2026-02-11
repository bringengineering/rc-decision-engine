"""Initial schema.

Revision ID: 001
Create Date: 2026-02-11
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column("provider", sa.String(50), server_default="local"),
        sa.Column("provider_id", sa.String(255), nullable=True),
        sa.Column("role", sa.String(20), server_default="engineer"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("safety_factor_target", sa.Float(), server_default="1.5"),
        sa.Column("location_code", sa.String(50), nullable=True),
        sa.Column("location_name", sa.String(200), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("bim_element_id", sa.String(255), nullable=True),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("geometry_json", postgresql.JSONB(), nullable=True),
        sa.Column("properties", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "calibration_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("physics_params", postgresql.JSONB(), server_default="{}"),
        sa.Column("drift_history", postgresql.JSONB(), server_default="[]"),
        sa.Column("last_calibrated_at", sa.DateTime(), nullable=True),
        sa.Column("calibration_count", sa.Integer(), server_default="0"),
        sa.Column("status", sa.String(20), server_default="uncalibrated"),
    )

    op.create_table(
        "simulation_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("simulation_type", sa.String(50), nullable=False),
        sa.Column("input_params", postgresql.JSONB(), server_default="{}"),
        sa.Column("climate_data", postgresql.JSONB(), server_default="{}"),
        sa.Column("status", sa.String(20), server_default="queued"),
        sa.Column("result", postgresql.JSONB(), nullable=True),
        sa.Column("mesh_file_url", sa.String(500), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "decision_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("simulation_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("simulation_runs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("failure_probability", sa.Float(), nullable=False),
        sa.Column("safety_factor_result", sa.Float(), nullable=False),
        sa.Column("safety_factor_target", sa.Float(), nullable=False),
        sa.Column("monte_carlo_n", sa.Integer(), server_default="1000"),
        sa.Column("ucl_95", sa.Float(), nullable=True),
        sa.Column("details", postgresql.JSONB(), server_default="{}"),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "sensor_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sensor_id", sa.String(100), nullable=False),
        sa.Column("sensor_type", sa.String(50), nullable=False),
        sa.Column("location_description", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("sensor_mappings")
    op.drop_table("decision_reports")
    op.drop_table("simulation_runs")
    op.drop_table("calibration_states")
    op.drop_table("assets")
    op.drop_table("projects")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
