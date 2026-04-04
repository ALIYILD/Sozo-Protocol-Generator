"""Add protocol_id to graph_runs for REST protocol linkage.

Revision ID: 003
Revises: 002
Create Date: 2026-04-04
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "graph_runs",
        sa.Column(
            "protocol_id",
            sa.String(36),
            sa.ForeignKey("protocols.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_graph_runs_protocol_id", "graph_runs", ["protocol_id"])


def downgrade() -> None:
    op.drop_index("ix_graph_runs_protocol_id", table_name="graph_runs")
    op.drop_column("graph_runs", "protocol_id")
