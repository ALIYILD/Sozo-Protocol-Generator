"""Celery task: run a LangGraph protocol generation pipeline off-request.

The task body is lifted from the synchronous logic that used to live
inline in ``sozo_api.server.generate_via_graph``. By relocating it into
a Celery worker we free the single uvicorn worker to keep serving HTTP
while long-running pipelines (evidence search, safety, composition)
execute in the background. The LangGraph SQLite checkpointer is shared
with the API process, so the existing ``GET /api/graph/status/{id}``
endpoint picks up progress automatically once the worker starts writing
checkpoints.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Optional

from sozo_api.celery_app import celery_app

logger = logging.getLogger(__name__)


def _set_graph_run_status(thread_id: str, status: str, error: Optional[str] = None) -> None:
    """Best-effort update of the GraphRun DB row's status column.

    Used to transition a pre-existing ``queued`` stub row into
    ``running`` / ``failed`` states so the polling endpoint can surface
    progress before the LangGraph checkpointer has any state to report.
    """
    try:
        from sozo_db.engine import get_session_factory
        from sozo_db.repositories.graph_run_repo import GraphRunRepository

        async def _run() -> None:
            factory = get_session_factory()
            async with factory() as session:
                repo = GraphRunRepository(session)
                run = await repo.get_by_thread_id(thread_id)
                if run is None:
                    return
                run.status = status
                if error:
                    # Append to errors list without clobbering existing.
                    existing = list(run.errors or [])
                    existing.append({"source": "celery_task", "message": error})
                    run.errors = existing
                await session.flush()
                await session.commit()

        asyncio.run(_run())
    except Exception as db_err:  # pragma: no cover — best-effort
        logger.warning(
            "GraphRun status update skipped for thread_id=%s status=%s: %s",
            thread_id,
            status,
            db_err,
        )


def _persist_final_state(state: dict) -> None:
    """Upsert a GraphRun row from the final LangGraph state (best-effort)."""
    try:
        from sozo_db.engine import get_session_factory
        from sozo_db.repositories.graph_run_repo import GraphRunRepository

        async def _run() -> None:
            factory = get_session_factory()
            async with factory() as session:
                repo = GraphRunRepository(session)
                existing = await repo.get_by_thread_id(
                    state.get("request_id", "")
                )
                if existing is None:
                    await repo.create(state)
                else:
                    await repo.update_from_state(
                        state.get("request_id", ""), state
                    )
                await session.commit()

        asyncio.run(_run())
    except Exception as db_err:  # pragma: no cover
        logger.warning("GraphRun final persist skipped: %s", db_err)


@celery_app.task(
    name="sozo_api.tasks.graph_generate.run_graph_generate",
    bind=True,
    acks_late=True,
    # Hard/soft limits: LangGraph pipelines normally finish in minutes,
    # but we give generous headroom so a slow evidence fetch doesn't get
    # killed. These can be tuned via env later.
    soft_time_limit=60 * 60,
    time_limit=60 * 60 + 300,
)
def run_graph_generate(
    self,
    thread_id: str,
    condition_slug: Optional[str],
    modality: Optional[str],
    tier: str,
    doc_type: str,
    prompt: Optional[str],
    patient_id: Optional[str],
    patient_context: Optional[dict],
    user_id: str,
    user_role: str,
) -> dict:
    """Run the unified LangGraph pipeline for a single request."""
    from sozo_api.graph_checkpointer import get_graph_checkpointer
    from sozo_graph.unified_graph import build_unified_graph, create_initial_state

    logger.info(
        "celery: run_graph_generate start thread_id=%s user_id=%s condition=%s",
        thread_id,
        user_id,
        condition_slug,
    )

    _set_graph_run_status(thread_id, "running")

    try:
        if prompt is not None and str(prompt).strip():
            effective_prompt = str(prompt).strip()
        elif condition_slug:
            effective_prompt = f"Generate {doc_type} for {condition_slug}"
        else:
            effective_prompt = f"Generate {doc_type}"

        structured: dict = {}
        if doc_type:
            structured["doc_type"] = doc_type
        if modality is not None:
            structured["modality"] = modality
        if patient_id is not None:
            structured["patient_id"] = patient_id
        if condition_slug:
            structured["condition_slug"] = condition_slug.strip()

        checkpointer = get_graph_checkpointer()
        graph = build_unified_graph(checkpointer=checkpointer)

        explicit_slug = condition_slug.strip() if condition_slug else None
        initial_state = create_initial_state(
            source_mode="prompt",
            user_prompt=effective_prompt,
            patient_context=patient_context,
            tier=tier,
            condition_slug=explicit_slug,
            normalized_request=structured or None,
        )
        # Force the caller-supplied thread_id so status polling works
        # against the same checkpoint key the HTTP handler already
        # returned to the client.
        initial_state["request_id"] = thread_id

        config = {"configurable": {"thread_id": thread_id}}

        result = graph.invoke(initial_state, config=config)

        _persist_final_state(result)

        try:
            from sozo_api.routes.audit_service import audit_service

            audit_service.log_event(
                entity_type="graph_run",
                entity_id=thread_id,
                action="generation_completed",
                actor=user_id,
                details={
                    "thread_id": thread_id,
                    "generation_method": "unified_graph_async",
                    "condition_slug": result.get("condition", {}).get("slug"),
                    "user_role": user_role,
                },
            )
        except Exception as audit_err:  # pragma: no cover
            logger.warning(
                "Audit log (graph_run complete) skipped: %s", audit_err
            )

        envelope: dict[str, Any] = {
            "thread_id": thread_id,
            "status": "complete",
            "protocol_id": (result.get("output") or {}).get("protocol_id"),
        }
        logger.info(
            "celery: run_graph_generate done thread_id=%s status=%s",
            thread_id,
            result.get("status"),
        )
        return envelope

    except Exception as exc:
        logger.exception(
            "celery: run_graph_generate failed thread_id=%s", thread_id
        )
        _set_graph_run_status(thread_id, "error", error=str(exc))
        return {
            "thread_id": thread_id,
            "status": "failed",
            "error": str(exc),
        }
