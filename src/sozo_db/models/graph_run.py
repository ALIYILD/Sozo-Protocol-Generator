"""GraphRun model — persists LangGraph pipeline executions."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Index, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base, UUIDMixin, TimestampMixin


class GraphRun(UUIDMixin, TimestampMixin, Base):
    """Record of a single LangGraph protocol generation run.

    Stores the final state snapshot, audit trail, and output references.
    The LangGraph checkpointer handles intermediate state persistence
    separately; this table stores the completed/reviewed run metadata.
    """
    __tablename__ = "graph_runs"

    thread_id: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    # intake | evidence | composition | review | approved | rejected | released | error

    # Condition
    condition_slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    condition_name: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Source
    source_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="prompt")
    user_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Evidence summary
    evidence_article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    evidence_sufficient: Mapped[bool | None] = mapped_column(nullable=True)
    evidence_grade_distribution: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Safety
    safety_cleared: Mapped[bool | None] = mapped_column(nullable=True)
    blocking_contraindications: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Protocol
    sections_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    grounding_score: Mapped[float | None] = mapped_column(nullable=True)
    composed_sections: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Review
    reviewer_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    review_decision: Mapped[str | None] = mapped_column(String(32), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Output
    output_paths: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    audit_record_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Full state snapshot (for reconstruction)
    final_state: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    node_history: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    errors: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Graph metadata
    graph_version: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Creator
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True,
    )

    __table_args__ = (
        Index("ix_graph_runs_status", "status"),
        Index("ix_graph_runs_condition", "condition_slug"),
        Index("ix_graph_runs_reviewer", "reviewer_id"),
    )

    def __repr__(self) -> str:
        return f"<GraphRun {self.thread_id[:8]}... {self.status} {self.condition_slug}>"
