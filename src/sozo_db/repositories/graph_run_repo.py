"""Repository for GraphRun persistence."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.graph_run import GraphRun

logger = logging.getLogger(__name__)


class GraphRunRepository:
    """CRUD operations for GraphRun records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, state: dict) -> GraphRun:
        """Create a GraphRun from a graph state dict."""
        condition = state.get("condition", {})
        evidence = state.get("evidence", {})
        safety = state.get("safety", {})
        protocol = state.get("protocol", {})
        review = state.get("review", {})
        output = state.get("output", {})

        run = GraphRun(
            thread_id=state.get("request_id", ""),
            status=state.get("status", "pending"),
            condition_slug=condition.get("slug", ""),
            condition_name=condition.get("display_name"),
            source_mode=state.get("source_mode", "prompt"),
            user_prompt=state.get("intake", {}).get("user_prompt"),
            evidence_article_count=len(evidence.get("articles", [])),
            evidence_sufficient=evidence.get("evidence_sufficient"),
            evidence_grade_distribution=evidence.get("evidence_summary", {}).get("grade_distribution"),
            safety_cleared=safety.get("safety_cleared"),
            blocking_contraindications=safety.get("blocking_contraindications"),
            sections_count=len(protocol.get("composed_sections", [])),
            grounding_score=protocol.get("grounding_score"),
            composed_sections=protocol.get("composed_sections"),
            reviewer_id=review.get("reviewer_id"),
            review_decision=review.get("status"),
            review_notes=review.get("review_notes"),
            revision_number=review.get("revision_number", 0),
            approved_at=(
                datetime.now(timezone.utc)
                if review.get("status") == "approved" else None
            ),
            output_paths=output.get("output_paths"),
            audit_record_id=output.get("audit_record_id"),
            final_state=state,
            node_history=state.get("node_history"),
            errors=state.get("errors"),
            graph_version=state.get("graph_version"),
        )

        self.session.add(run)
        await self.session.flush()
        logger.info("Created GraphRun %s for %s", run.thread_id[:8], run.condition_slug)
        return run

    async def get_by_thread_id(self, thread_id: str) -> Optional[GraphRun]:
        """Get a GraphRun by thread_id."""
        result = await self.session.execute(
            select(GraphRun).where(GraphRun.thread_id == thread_id)
        )
        return result.scalar_one_or_none()

    async def update_from_state(self, thread_id: str, state: dict) -> Optional[GraphRun]:
        """Update an existing GraphRun from new graph state."""
        run = await self.get_by_thread_id(thread_id)
        if not run:
            return None

        review = state.get("review", {})
        output = state.get("output", {})
        protocol = state.get("protocol", {})

        run.status = state.get("status", run.status)
        run.reviewer_id = review.get("reviewer_id") or run.reviewer_id
        run.review_decision = review.get("status") or run.review_decision
        run.review_notes = review.get("review_notes") or run.review_notes
        run.revision_number = review.get("revision_number", run.revision_number)
        run.output_paths = output.get("output_paths") or run.output_paths
        run.audit_record_id = output.get("audit_record_id") or run.audit_record_id
        run.composed_sections = protocol.get("composed_sections") or run.composed_sections
        run.grounding_score = protocol.get("grounding_score") or run.grounding_score
        run.final_state = state
        run.node_history = state.get("node_history")
        run.errors = state.get("errors")

        if review.get("status") == "approved":
            run.approved_at = datetime.now(timezone.utc)

        await self.session.flush()
        return run

    async def list_runs(
        self,
        condition_slug: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[GraphRun]:
        """List GraphRuns with optional filters."""
        query = select(GraphRun).order_by(GraphRun.created_at.desc())

        if condition_slug:
            query = query.where(GraphRun.condition_slug == condition_slug)
        if status:
            query = query.where(GraphRun.status == status)

        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        condition_slug: Optional[str] = None,
        status: Optional[str] = None,
    ) -> int:
        """Count GraphRuns with optional filters."""
        from sqlalchemy import func as sa_func
        query = select(sa_func.count(GraphRun.id))
        if condition_slug:
            query = query.where(GraphRun.condition_slug == condition_slug)
        if status:
            query = query.where(GraphRun.status == status)
        result = await self.session.execute(query)
        return result.scalar_one()
