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
    # SQLite can't ALTER TABLE to add FK constraints; use batch mode copy+move.
    with op.batch_alter_table("graph_runs") as batch_op:
        batch_op.add_column(
            sa.Column(
                "protocol_id",
                sa.String(36),
                sa.ForeignKey(
                    "protocols.id",
                    name="fk_graph_runs_protocol_id_protocols",
                    ondelete="SET NULL",
                ),
                nullable=True,
            )
        )
        batch_op.create_index(
            "ix_graph_runs_protocol_id",
            ["protocol_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("graph_runs") as batch_op:
        batch_op.drop_index("ix_graph_runs_protocol_id")
        batch_op.drop_column("protocol_id")
