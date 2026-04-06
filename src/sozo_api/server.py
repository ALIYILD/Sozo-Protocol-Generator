"""
SOZO API Server — FastAPI HTTP endpoints for visualization, generation,
knowledge, and cockpit services.

Requires: fastapi, uvicorn
Install with:  pip install fastapi uvicorn

Run with:
    uvicorn sozo_api.server:app --reload --port 8000
"""
from __future__ import annotations

import io
import logging
import uuid
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

# --- Conditional FastAPI import ---------------------------------------------------
# FastAPI may not be installed in all environments. The module remains valid Python
# regardless; callers get a clear ImportError with install instructions if missing.
try:
    from fastapi import Depends, FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel
except ImportError as _exc:
    raise ImportError(
        "FastAPI is required but not installed. "
        "Install it with:  pip install fastapi uvicorn"
    ) from _exc

from sqlalchemy import text as sa_text

from sozo_api.error_responses import INTERNAL_SERVER_DETAIL

logger = logging.getLogger(__name__)

# ── Pydantic request models (thin wrappers for non-schema endpoints) ──────

class CanonicalGenerateRequest(BaseModel):
    """Request body for POST /api/generate/canonical."""
    condition: str
    doc_type: str = "evidence_based_protocol"
    tier: str = "fellow"


class GraphGenerateRequest(BaseModel):
    """Request body for graph-based protocol generation."""
    condition_slug: Optional[str] = None
    modality: Optional[str] = None
    tier: str = "fellow"
    doc_type: str = "evidence_based_protocol"
    prompt: Optional[str] = None
    patient_id: Optional[str] = None
    patient_context: Optional[dict] = None


class GraphReviewRequest(BaseModel):
    """Request body for clinician review action on a graph run."""
    thread_id: str
    decision: str  # approve | reject | edit
    reviewer_id: str
    reviewer_credentials: str = ""
    review_notes: str = ""
    section_edits: Optional[list] = None
    parameter_overrides: Optional[list] = None
    #: Optional REST `protocols.id` to attach when submitting review.
    protocol_id: Optional[str] = None


class GraphLinkProtocolRequest(BaseModel):
    """Attach an existing REST protocol row to a graph run (checkpoint + DB)."""
    thread_id: str
    protocol_id: str


# ── App factory ───────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""

    # Fail fast for production-like profiles (JWT secret, CORS).
    from sozo_auth.config import AuthConfig, auth_config
    from sozo_auth.dependencies import (
        require_clinician,
        require_reviewer,
        require_role,
    )
    from sozo_auth.models import UserResponse
    from sozo_api.cors_config import resolve_cors_allow_origins_and_credentials

    _require_operator_or_admin = [Depends(require_role("operator", "admin"))]
    _require_clinician = [Depends(require_clinician)]

    # Validate against the **current** process environment (not only the import-time
    # singleton), so a second create_app() under tests or dynamic reload still enforces secrets.
    AuthConfig()
    _ = auth_config

    cors_origins, cors_credentials = resolve_cors_allow_origins_and_credentials()

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        logger.info("SOZO API started")
        try:
            import os
            import subprocess
            from pathlib import Path
            alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
            if not alembic_ini.exists():
                logger.warning("alembic.ini not found at %s", alembic_ini)
            else:
                env = os.environ.copy()
                env.setdefault("PYTHONPATH", "/app/src")

                def _run_alembic(*args: str) -> subprocess.CompletedProcess[str]:
                    return subprocess.run(
                        ["alembic", "-c", str(alembic_ini), *args],
                        cwd=str(alembic_ini.parent),
                        env=env,
                        capture_output=True,
                        text=True,
                        timeout=60,
                    )

                result = _run_alembic("upgrade", "head")
                if result.returncode == 0:
                    logger.info("Database migration complete")
                elif "already exists" in (result.stderr or ""):
                    logger.warning(
                        "Alembic upgrade hit 'already exists' — DB has tables "
                        "without a version stamp. Stamping head and retrying."
                    )
                    stamp = _run_alembic("stamp", "head")
                    if stamp.returncode == 0:
                        retry = _run_alembic("upgrade", "head")
                        if retry.returncode == 0:
                            logger.info(
                                "Database migration complete after stamp+retry"
                            )
                        else:
                            logger.warning(
                                "Alembic retry after stamp failed: %s",
                                (retry.stderr or "")[-500:],
                            )
                    else:
                        logger.warning(
                            "Alembic stamp head failed: %s",
                            (stamp.stderr or "")[-500:],
                        )
                else:
                    logger.warning(
                        "Alembic upgrade returned %s; stderr=%s",
                        result.returncode,
                        (result.stderr or "")[-500:],
                    )
        except Exception as exc:
            logger.warning("Auto-migration skipped: %s", exc)

        try:
            from sozo_db.base import Base
            from sozo_db.engine import get_engine

            import sozo_db.models  # noqa: F401

            engine = get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Base.metadata.create_all completed (idempotent backstop)")
        except Exception as exc:
            logger.warning("Base.metadata.create_all skipped: %s", exc)

        try:
            from sozo_auth.router import _insert_user
            from sozo_auth.passwords import hash_password
            from sozo_db.engine import get_session_factory
            from sozo_db.models.user import User
            from sqlalchemy import func, select
            from datetime import datetime, timezone
            import uuid as _uuid

            factory = get_session_factory()
            async with factory() as session:
                count = (await session.execute(select(func.count()).select_from(User))).scalar_one()

            if count == 0:
                now = datetime.now(timezone.utc)
                await _insert_user({
                    "id": _uuid.uuid4().hex,
                    "email": "demo@sozo.app",
                    "name": "Demo Clinician",
                    "role": "clinician",
                    "active": True,
                    "created_at": now,
                    "password_hash": hash_password("SozoDemo2026!"),
                })
                await _insert_user({
                    "id": _uuid.uuid4().hex,
                    "email": "admin@sozo.app",
                    "name": "Demo Admin",
                    "role": "admin",
                    "active": True,
                    "created_at": now,
                    "password_hash": hash_password("SozoAdmin2026!"),
                })
                logger.info(
                    "Seeded demo users: demo@sozo.app/SozoDemo2026! (clinician), "
                    "admin@sozo.app/SozoAdmin2026! (admin)"
                )
        except Exception as exc:
            logger.warning("Demo user seeding skipped: %s", exc)

        yield

    application = FastAPI(
        title="SOZO Protocol API",
        version="1.0.0",
        description="HTTP interface for SOZO visualization, generation, knowledge, and cockpit services.",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=cors_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Router includes ──────────────────────────────────────────────
    from sozo_api.routes.protocols import router as protocols_router
    from sozo_api.routes.patients import router as patients_router
    from sozo_api.routes.reviews import router as reviews_router
    from sozo_api.routes.audit import router as audit_router
    from sozo_api.routes.template_batch import router as template_batch_router

    try:
        from sozo_auth import auth_router
        application.include_router(auth_router, prefix="/api")
    except ImportError:
        logger.warning("sozo_auth not available — auth endpoints disabled")

    application.include_router(protocols_router)
    application.include_router(patients_router)
    application.include_router(reviews_router)
    application.include_router(audit_router)
    application.include_router(template_batch_router)

    # ── Health ────────────────────────────────────────────────────────

    @application.get("/api/health")
    async def health() -> dict:
        import os as _os
        checks: dict[str, Any] = {"api": "ok"}
        # DB check
        try:
            from sozo_db.engine import get_engine
            engine = get_engine()
            async with engine.connect() as conn:
                await conn.execute(sa_text("SELECT 1"))
            checks["database"] = "ok"
        except Exception:
            logger.warning("Health check: database unreachable", exc_info=True)
            checks["database"] = "unavailable"

        # Graph check
        try:
            from sozo_graph.unified_graph import build_unified_graph
            build_unified_graph()  # compile check
            checks["graph"] = "ok"
        except Exception:
            logger.warning("Health check: graph compile failed", exc_info=True)
            checks["graph"] = "unavailable"

        # API key presence (booleans, not gated in overall status so a
        # missing key produces a "degraded" warning but never a hard fail).
        checks["anthropic_key_configured"] = bool(_os.environ.get("ANTHROPIC_API_KEY"))
        checks["semantic_scholar_key_configured"] = bool(
            _os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        )

        string_checks = {k: v for k, v in checks.items() if isinstance(v, str)}
        overall = "ok" if all(v == "ok" for v in string_checks.values()) else "degraded"
        if not checks["anthropic_key_configured"]:
            overall = "degraded"
        return {"status": overall, "checks": checks}

    # ── Visuals ───────────────────────────────────────────────────────

    @application.get("/api/visuals/types")
    async def list_visual_types() -> dict:
        """List all supported visualization types."""
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        return {"types": svc.list_types()}

    @application.post(
        "/api/visuals/render",
        dependencies=_require_clinician,
    )
    async def render_visual(request_body: dict[str, Any]) -> Any:
        """Render a visualization from a VisualizationRequest JSON body.

        Returns PNG bytes (as streaming response) when render_format is "png",
        or a JSON envelope with metadata, explanation, and evidence otherwise.
        """
        from sozo_visuals.schemas import VisualizationRequest, RenderFormat
        from sozo_visuals.service import VisualizationService

        try:
            req = VisualizationRequest(**request_body)
        except Exception:
            logger.warning("Visual render: invalid request body", exc_info=True)
            raise HTTPException(
                status_code=422,
                detail="Invalid visualization request body.",
            )

        svc = VisualizationService()
        response = svc.render(req)

        if not response.success:
            raise HTTPException(status_code=500, detail=response.error or "Render failed")

        # Build the JSON metadata envelope (always useful).
        json_envelope: dict[str, Any] = {
            "visual_id": response.visual_id,
            "visual_type": response.visual_type,
            "render_format": response.render_format,
            "generated_at": response.generated_at,
            "confidence": response.confidence,
            "success": response.success,
            "warnings": response.warnings,
            "explanation": response.explanation.model_dump(),
            "evidence": [e.model_dump() for e in response.evidence],
            "metadata": response.metadata.model_dump(),
        }

        # PNG-only: stream the image; attach JSON metadata as a custom header.
        if req.render_format == RenderFormat.PNG:
            if not response.image_bytes:
                raise HTTPException(status_code=500, detail="Render produced no image bytes")
            import json as _json
            headers = {
                "X-Sozo-Visual-Meta": _json.dumps(json_envelope, default=str),
            }
            return StreamingResponse(
                io.BytesIO(response.image_bytes),
                media_type="image/png",
                headers=headers,
            )

        # plotly_json or both: return full JSON.
        if response.plotly_json:
            json_envelope["plotly_json"] = response.plotly_json
        if response.image_path:
            json_envelope["image_path"] = response.image_path
        return JSONResponse(content=json_envelope)

    # ── Visuals Library (pre-rendered PNGs) ──────────────────────────

    _VISUALS_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs" / "visuals"

    _VISUAL_TYPE_MAP = {
        "brain_map": "Brain Map",
        "network_diagram": "Network Diagram",
        "symptom_flow": "Symptom Flow",
        "patient_journey": "Patient Journey",
    }

    def _condition_display_name(slug: str) -> str:
        """Convert slug to a human-readable name."""
        return slug.replace("_", " ").title()

    def _infer_visual_type(filename: str) -> str:
        """Derive a visual type key from a filename."""
        stem = filename.replace(".png", "")
        for key in _VISUAL_TYPE_MAP:
            if stem.endswith(key):
                return key
        # Fallback: use the part after the condition slug
        parts = stem.split("_")
        if len(parts) >= 2:
            return "_".join(parts[1:])
        return "other"

    @application.get("/api/visuals/library")
    async def list_visuals_library(condition: str = "", visual_type: str = "") -> dict:
        """Return a manifest of all pre-rendered PNG visuals in outputs/visuals/.

        Each entry has: condition, condition_name, visual_type, visual_type_label,
        filename, url (relative path for browser fetch).
        """
        from fastapi.responses import JSONResponse as _JSON

        items: list[dict] = []

        if not _VISUALS_OUTPUT_DIR.exists():
            return {"items": items, "total": 0}

        for cond_dir in sorted(_VISUALS_OUTPUT_DIR.iterdir()):
            if not cond_dir.is_dir():
                continue
            cond_slug = cond_dir.name
            if condition and cond_slug != condition:
                continue

            # PNGs may sit directly in cond_dir OR in cond_dir/visuals/
            search_dirs = [cond_dir, cond_dir / "visuals"]
            for search_dir in search_dirs:
                if not search_dir.is_dir():
                    continue
                for png in sorted(search_dir.glob("*.png")):
                    vtype = _infer_visual_type(png.name)
                    if visual_type and vtype != visual_type:
                        continue
                    # Build a URL the frontend can use to fetch the image
                    rel = png.relative_to(_VISUALS_OUTPUT_DIR)
                    url = f"/api/visuals/file/{rel.as_posix()}"
                    items.append({
                        "condition": cond_slug,
                        "condition_name": _condition_display_name(cond_slug),
                        "visual_type": vtype,
                        "visual_type_label": _VISUAL_TYPE_MAP.get(vtype, vtype.replace("_", " ").title()),
                        "filename": png.name,
                        "url": url,
                    })

        return {"items": items, "total": len(items)}

    @application.get("/api/visuals/file/{file_path:path}")
    async def serve_visual_file(file_path: str) -> Any:
        """Serve a pre-rendered PNG from outputs/visuals/."""
        from fastapi.responses import FileResponse as _FR
        import re as _re

        # Safety: reject any path traversal attempts
        if ".." in file_path or _re.search(r"[\\:]", file_path):
            raise HTTPException(status_code=400, detail="Invalid path")

        abs_path = _VISUALS_OUTPUT_DIR / file_path
        if not abs_path.exists() or not abs_path.is_file():
            raise HTTPException(status_code=404, detail="Visual not found")

        return _FR(str(abs_path), media_type="image/png")

    # ── Generation ────────────────────────────────────────────────────

    @application.post(
        "/api/generate/canonical",
        dependencies=_require_clinician,
    )
    async def generate_canonical(body: CanonicalGenerateRequest) -> dict:
        """Generate a document via the canonical blueprint-driven path."""
        from sozo_generator.generation.service import GenerationService

        svc = GenerationService()
        result = svc.generate_canonical(
            condition=body.condition,
            doc_type=body.doc_type,
            tier=body.tier,
        )

        if not result.success:
            raise HTTPException(
                status_code=400,
                detail=result.error or "Generation failed",
            )

        return {
            "success": result.success,
            "output_path": result.output_path,
            "build_id": result.build_id,
        }

    # ── Knowledge ─────────────────────────────────────────────────────

    def _get_kb():
        """Lazy-load the KnowledgeBase singleton per request."""
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        return kb

    @application.get("/api/knowledge/conditions")
    async def list_conditions() -> dict:
        """List all conditions with summary fields."""
        kb = _get_kb()
        items = []
        for slug in kb.list_conditions():
            cond = kb.get_condition(slug)
            if cond:
                items.append({
                    "slug": cond.slug,
                    "display_name": cond.display_name,
                    "icd10": cond.icd10,
                    "category": cond.category,
                })
        return {"conditions": items}

    @application.get("/api/knowledge/conditions/{slug}")
    async def get_condition(slug: str) -> dict:
        """Return full knowledge object for a condition."""
        kb = _get_kb()
        cond = kb.get_condition(slug)
        if not cond:
            raise HTTPException(status_code=404, detail=f"Condition not found: {slug}")
        return {"condition": cond.model_dump()}

    # ── Cockpit ───────────────────────────────────────────────────────

    @application.get(
        "/api/cockpit/overview",
        dependencies=_require_operator_or_admin,
    )
    async def cockpit_overview() -> dict:
        """Platform-wide operational overview."""
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        ov = svc.overview()
        return {"overview": asdict(ov)}

    @application.get(
        "/api/cockpit/conditions",
        dependencies=_require_operator_or_admin,
    )
    async def cockpit_conditions() -> dict:
        """Per-condition operational summaries."""
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        summaries = svc.conditions_summary()
        return {"conditions": [asdict(s) for s in summaries]}

    # ── Shared graph checkpointer ────────────────────────────────────────
    from sozo_api.graph_checkpointer import get_graph_checkpointer

    # ── Graph-based generation ─────────────────────────────────────────

    @application.post("/api/graph/generate")
    async def generate_via_graph(
        body: GraphGenerateRequest,
        current_user: UserResponse = Depends(require_clinician),
    ) -> dict:
        """Enqueue a protocol generation pipeline on the Celery worker.

        The LangGraph pipeline (evidence search, safety, composition,
        clinician-review interrupt) runs in a background Celery worker
        process with a local Redis broker, so the single uvicorn worker
        is never blocked for minutes. This endpoint returns immediately
        with a ``thread_id``; the client polls
        ``GET /api/graph/status/{thread_id}`` for progress. The worker
        writes to the same LangGraph SQLite checkpointer, so polling
        surfaces state transitions transparently once execution starts.
        """
        # Lazy import: avoids pulling celery/redis client into the cold
        # path of unrelated endpoints.
        from sozo_api.tasks.graph_generate import run_graph_generate

        logger.info("Graph generate enqueue for user_id=%s", current_user.id)

        try:
            # Input validation — same spirit as the previous handler.
            if body.condition_slug is not None and not body.condition_slug.strip():
                raise HTTPException(
                    status_code=400, detail="condition_slug cannot be blank"
                )
            if (
                (body.prompt is None or not str(body.prompt).strip())
                and not body.condition_slug
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Either prompt or condition_slug is required",
                )

            thread_id = str(uuid.uuid4())

            # Best-effort: insert a 'queued' stub GraphRun row so the
            # status endpoint can report queued/running state before the
            # LangGraph checkpointer has written anything.
            try:
                from sozo_db.repositories.graph_run_repo import GraphRunRepository
                from sozo_db.engine import get_session_factory

                stub_state = {
                    "request_id": thread_id,
                    "status": "queued",
                    "source_mode": "prompt",
                    "condition": {
                        "slug": (body.condition_slug or "").strip(),
                        "display_name": None,
                    },
                    "intake": {"user_prompt": body.prompt or ""},
                    "evidence": {},
                    "safety": {},
                    "protocol": {},
                    "review": {},
                    "output": {},
                    "node_history": [],
                    "errors": [],
                }
                factory = get_session_factory()
                async with factory() as session:
                    repo = GraphRunRepository(session)
                    await repo.create(stub_state)
                    await session.commit()
            except Exception as db_err:
                logger.warning(
                    "GraphRun queued-stub persist skipped: %s", db_err
                )

            async_result = run_graph_generate.delay(
                thread_id=thread_id,
                condition_slug=body.condition_slug,
                modality=body.modality,
                tier=body.tier,
                doc_type=body.doc_type,
                prompt=body.prompt,
                patient_id=body.patient_id,
                patient_context=body.patient_context,
                user_id=str(current_user.id),
                user_role=getattr(current_user, "role", "clinician") or "clinician",
            )

            try:
                from sozo_api.routes.audit_service import audit_service

                audit_service.log_event(
                    entity_type="graph_run",
                    entity_id=thread_id,
                    action="generation_enqueued",
                    actor=current_user.email,
                    details={
                        "thread_id": thread_id,
                        "generation_method": "unified_graph_async",
                        "celery_task_id": async_result.id,
                        "condition_slug": (body.condition_slug or None),
                    },
                )
            except Exception as audit_err:
                logger.warning(
                    "Audit log (graph_run enqueue) skipped: %s", audit_err
                )

            return {
                "success": True,
                "thread_id": thread_id,
                "status": "queued",
                "task_id": async_result.id,
            }
        except HTTPException:
            raise
        except Exception:
            logger.exception("Graph generation enqueue failed")
            raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)

    @application.get("/api/graph/status/{thread_id}")
    async def graph_status(
        thread_id: str,
        _user: UserResponse = Depends(require_clinician),
    ) -> dict:
        """Get the current status of a graph execution by thread_id.

        Returns the full review payload if the graph is paused at the
        clinician review interrupt.
        """
        from sozo_graph.unified_graph import build_unified_graph

        try:
            checkpointer = get_graph_checkpointer()
            graph = build_unified_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}

            state = graph.get_state(config)
            if not state or not state.values:
                # No LangGraph checkpoint yet — the Celery worker may not
                # have started executing. Fall back to the GraphRun DB
                # row for queued/running visibility before the first
                # checkpoint is written.
                try:
                    from sozo_db.repositories.graph_run_repo import GraphRunRepository
                    from sozo_db.engine import get_session_factory

                    factory = get_session_factory()
                    async with factory() as session:
                        repo = GraphRunRepository(session)
                        db_run = await repo.get_by_thread_id(thread_id)
                        if db_run is not None:
                            db_hist = list(db_run.node_history or [])
                            return {
                                "thread_id": thread_id,
                                "status": db_run.status or "queued",
                                "status_source": "graph_run_db",
                                "protocol_id": (
                                    str(db_run.protocol_id)
                                    if db_run.protocol_id else None
                                ),
                                "review_status": "pending",
                                "revision_number": db_run.revision_number or 0,
                                "condition": {
                                    "slug": db_run.condition_slug,
                                    "display_name": db_run.condition_name,
                                },
                                "evidence": {},
                                "safety": {},
                                "protocol": {"sections": []},
                                "evidence_articles": [],
                                "node_history": [
                                    {
                                        "node_id": n.get("node_id") or n.get("node_name"),
                                        "duration_ms": n.get("duration_ms"),
                                        "status": n.get("status"),
                                        "started_at": n.get("started_at"),
                                        "completed_at": n.get("completed_at"),
                                        "source": n.get("source"),
                                    }
                                    for n in db_hist
                                ],
                                "output": {},
                            }
                except HTTPException:
                    raise
                except Exception:
                    logger.debug(
                        "graph_status queued-row fallback failed",
                        exc_info=True,
                    )
                raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

            values = state.values
            review = values.get("review", {})
            evidence = values.get("evidence", {})
            safety = values.get("safety", {})
            protocol = values.get("protocol", {})
            output_state = dict(values.get("output") or {})

            # Always consult the GraphRun row so that (a) we can surface
            # the protocol_id when the checkpointer hasn't seen it yet,
            # and (b) we can report fine-grained in-node progress from
            # the node_tracker decorator between sparse LangGraph
            # checkpoint writes.
            db_run = None
            try:
                from sozo_db.repositories.graph_run_repo import GraphRunRepository
                from sozo_db.engine import get_session_factory

                factory = get_session_factory()
                async with factory() as session:
                    repo = GraphRunRepository(session)
                    db_run = await repo.get_by_thread_id(thread_id)
                    if db_run and db_run.protocol_id and not output_state.get("protocol_id"):
                        output_state["protocol_id"] = str(db_run.protocol_id)
            except Exception:
                logger.debug(
                    "graph_status GraphRun lookup failed",
                    exc_info=True,
                )

            checkpoint_history = list(values.get("node_history") or [])
            db_history = list((db_run.node_history or []) if db_run else [])
            # Prefer DB history when it has more entries — the
            # node_tracker decorator writes row-level progress on every
            # node entry/exit, while LangGraph only checkpoints at
            # sparse boundaries, so a running super-node is only visible
            # through the DB row.
            if len(db_history) > len(checkpoint_history):
                effective_history = db_history
                _history_source = "graph_run_db"
            else:
                effective_history = checkpoint_history
                _history_source = "checkpointer"

            # Status: terminal states from either source win; otherwise
            # if the DB row says running and the last history entry is
            # not a terminal node_tracker "failed" entry, report running.
            ckpt_status = values.get("status", "unknown")
            db_status = (db_run.status if db_run else None) or None
            terminal_states = {"complete", "approved", "released", "error", "rejected", "failed"}
            if ckpt_status in terminal_states:
                effective_status = ckpt_status
            elif db_status in terminal_states:
                effective_status = db_status
            elif db_status == "running":
                effective_status = "running"
            else:
                effective_status = ckpt_status or db_status or "unknown"

            return {
                "thread_id": thread_id,
                "status": effective_status,
                "status_source": _history_source,
                "protocol_id": output_state.get("protocol_id"),
                "review_status": review.get("status", "pending"),
                "revision_number": review.get("revision_number", 0),
                "condition": {
                    "slug": values.get("condition", {}).get("slug"),
                    "display_name": values.get("condition", {}).get("display_name"),
                },
                "evidence": {
                    "sufficient": evidence.get("evidence_sufficient"),
                    "article_count": len(evidence.get("articles", [])),
                    "grade_distribution": evidence.get("evidence_summary", {}).get("grade_distribution", {}),
                    "gaps": evidence.get("evidence_gaps", []),
                },
                "safety": {
                    "cleared": safety.get("safety_cleared"),
                    "blocking": safety.get("blocking_contraindications", []),
                    "off_label": safety.get("off_label_flags", []),
                    "consent": safety.get("consent_requirements", []),
                },
                "protocol": {
                    "sections": [
                        {
                            "section_id": s.get("section_id"),
                            "title": s.get("title"),
                            "content": s.get("content", "")[:500],
                            "cited_evidence_ids": s.get("cited_evidence_ids", []),
                            "confidence": s.get("confidence"),
                        }
                        for s in protocol.get("composed_sections", [])
                    ],
                    "grounding_score": protocol.get("grounding_score"),
                    "grounding_issues": protocol.get("grounding_issues", []),
                },
                "evidence_articles": [
                    {
                        "pmid": a.get("pmid"),
                        "doi": a.get("doi"),
                        "title": a.get("title"),
                        "year": a.get("year"),
                        "grade": a.get("evidence_grade"),
                        "authors": a.get("authors", [])[:3],
                    }
                    for a in evidence.get("articles", [])[:20]
                ],
                "node_history": [
                    {
                        "node_id": n.get("node_id") or n.get("node_name"),
                        "duration_ms": n.get("duration_ms"),
                        "status": n.get("status"),
                        "started_at": n.get("started_at"),
                        "completed_at": n.get("completed_at"),
                        "source": n.get("source"),
                    }
                    for n in effective_history
                ],
                "output": output_state,
            }

        except HTTPException:
            raise
        except Exception:
            logger.exception("Graph status check failed")
            raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)

    @application.post("/api/graph/link-protocol")
    async def link_graph_protocol(
        body: GraphLinkProtocolRequest,
        _user: UserResponse = Depends(require_clinician),
    ) -> dict:
        """Attach a REST protocol id to a graph run (checkpoint `output` + GraphRun row)."""
        from sozo_graph.unified_graph import build_unified_graph

        try:
            try:
                pid = uuid.UUID(body.protocol_id.strip())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid protocol_id")

            checkpointer = get_graph_checkpointer()
            graph = build_unified_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": body.thread_id}}
            state = graph.get_state(config)
            if not state or not state.values:
                raise HTTPException(
                    status_code=404,
                    detail=f"Thread {body.thread_id} not found",
                )

            merged = dict(state.values.get("output") or {})
            merged["protocol_id"] = str(pid)
            graph.update_state(config, {"output": merged})

            try:
                from sozo_db.repositories.graph_run_repo import GraphRunRepository
                from sozo_db.engine import get_session_factory

                factory = get_session_factory()
                async with factory() as session:
                    repo = GraphRunRepository(session)
                    await repo.set_protocol_id(body.thread_id, pid)
                    await session.commit()
            except Exception as db_err:
                logger.warning("GraphRun protocol link DB persist skipped: %s", db_err)

            return {
                "success": True,
                "thread_id": body.thread_id,
                "protocol_id": str(pid),
            }
        except HTTPException:
            raise
        except Exception:
            logger.exception("Graph protocol link failed")
            raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)

    @application.post("/api/graph/review")
    async def submit_graph_review(
        body: GraphReviewRequest,
        current_user: UserResponse = Depends(require_reviewer),
    ) -> dict:
        """Submit a clinician review decision and resume the graph.

        The graph will:
        - On approve: render output documents and write audit record
        - On reject: terminate (or re-compose if under max revisions)
        - On edit: apply edits and loop back to review
        """
        from sozo_graph.unified_graph import build_unified_graph
        from datetime import datetime, timezone

        try:
            checkpointer = get_graph_checkpointer()
            graph = build_unified_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": body.thread_id}}

            # Verify thread exists
            state = graph.get_state(config)
            if not state or not state.values:
                raise HTTPException(status_code=404, detail=f"Thread {body.thread_id} not found")

            now = datetime.now(timezone.utc).isoformat()
            current_revision = state.values.get("review", {}).get("revision_number", 0)

            # Map decision to status
            status_map = {"approve": "approved", "reject": "rejected", "edit": "edited"}
            review_status = status_map.get(body.decision, body.decision)

            update_payload: dict[str, Any] = {
                "review": {
                    "status": review_status,
                    "reviewer_id": current_user.id,
                    "reviewer_credentials": body.reviewer_credentials,
                    "review_timestamp": now,
                    "review_notes": body.review_notes,
                    "revision_number": current_revision,
                    "edits_applied": body.section_edits or [],
                    "parameter_overrides": body.parameter_overrides or [],
                },
            }
            if body.protocol_id is not None and str(body.protocol_id).strip():
                try:
                    link_pid = uuid.UUID(str(body.protocol_id).strip())
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid protocol_id")
                out = dict(state.values.get("output") or {})
                out["protocol_id"] = str(link_pid)
                update_payload["output"] = out

            graph.update_state(config, update_payload)

            # Resume graph execution
            result = graph.invoke(None, config=config)

            try:
                from sozo_db.repositories.graph_run_repo import GraphRunRepository
                from sozo_db.engine import get_session_factory

                factory = get_session_factory()
                async with factory() as session:
                    repo = GraphRunRepository(session)
                    await repo.update_from_state(body.thread_id, result)
                    await session.commit()
            except Exception as db_err:
                logger.warning("GraphRun DB update after review skipped: %s", db_err)

            try:
                from sozo_api.routes.audit_service import audit_service

                audit_service.log_event(
                    entity_type="graph_run",
                    entity_id=body.thread_id,
                    action="graph_review_submitted",
                    actor=current_user.email,
                    details={
                        "thread_id": body.thread_id,
                        "decision": body.decision,
                        "review_status": review_status,
                        "reviewer_id": current_user.id,
                        "protocol_id": result.get("output", {}).get("protocol_id"),
                    },
                )
            except Exception as audit_err:
                logger.warning("Audit log (graph review) skipped: %s", audit_err)

            return {
                "success": True,
                "thread_id": body.thread_id,
                "decision": body.decision,
                "status": result.get("status", "unknown"),
                "revision_number": result.get("review", {}).get("revision_number", 0),
                "output": result.get("output", {}),
                "audit_record_id": result.get("output", {}).get("audit_record_id"),
                "protocol_id": result.get("output", {}).get("protocol_id"),
            }

        except HTTPException:
            raise
        except Exception:
            logger.exception("Graph review submission failed")
            raise HTTPException(status_code=500, detail=INTERNAL_SERVER_DETAIL)

    # Keep legacy endpoint as alias
    @application.post("/api/generate/graph")
    async def generate_via_graph_legacy(
        body: GraphGenerateRequest,
        current_user: UserResponse = Depends(require_clinician),
    ) -> dict:
        """Legacy alias for /api/graph/generate."""
        return await generate_via_graph(body, current_user)

    # ── Evidence staleness ─────────────────────────────────────────────

    @application.get(
        "/api/evidence/staleness",
        dependencies=_require_operator_or_admin,
    )
    async def evidence_staleness() -> dict:
        """Get evidence freshness report across all conditions."""
        from sozo_generator.evidence.staleness import get_staleness_report
        report = get_staleness_report()
        return {
            "overall_health": report.overall_health,
            "total_conditions": report.total_conditions,
            "fresh": report.fresh_count,
            "aging": report.aging_count,
            "stale": report.stale_count,
            "expired": report.expired_count,
            "high_priority_refreshes": report.high_priority_refreshes,
            "conditions": [
                {
                    "slug": c.condition_slug,
                    "name": c.condition_name,
                    "freshness": c.freshness.value,
                    "days_since_search": c.days_since_search,
                    "evidence_level": c.evidence_level,
                    "needs_refresh": c.needs_refresh,
                }
                for c in report.conditions
            ],
        }

    # ── Safety check endpoint ──────────────────────────────────────────

    @application.post(
        "/api/safety/check",
        dependencies=_require_clinician,
    )
    async def safety_check(body: dict) -> dict:
        """Run patient safety evaluation."""
        from sozo_generator.safety import evaluate_patient_safety

        result = evaluate_patient_safety(
            patient_demographics=body.get("demographics", {}),
            medications=body.get("medications", []),
            medical_history=body.get("medical_history", []),
            target_modalities=body.get("modalities"),
        )
        return {
            "safety_cleared": result.safety_cleared,
            "absolute_contraindications": result.absolute_contraindications,
            "relative_contraindications": result.relative_contraindications,
            "modality_clearance": result.modality_clearance,
            "warnings": result.warnings,
            "medication_summary": result.medication_interactions.summary,
        }

    # ── Personalization endpoint ───────────────────────────────────────

    @application.post(
        "/api/personalization/run",
        dependencies=_require_clinician,
    )
    async def run_personalization(body: dict) -> dict:
        """Run the personalization engine for a patient."""
        from sozo_personalization import PersonalizationEngine
        from sozo_personalization.models import PersonalizationRequest

        # Load condition schema for personalization
        condition_slug = body["condition_slug"]
        kb = _get_kb()
        cond = kb.get_condition(condition_slug)
        condition_schema = cond.model_dump() if cond else {"slug": condition_slug}

        engine = PersonalizationEngine(condition_schema=condition_schema)
        request = PersonalizationRequest(
            condition_slug=body["condition_slug"],
            patient_demographics=body.get("demographics", {}),
            symptoms=body.get("symptoms", []),
            medications=body.get("medications", []),
            treatment_history=body.get("treatment_history", []),
            medical_history=body.get("medical_history", []),
            eeg_features=body.get("eeg_features"),
            target_modalities=body.get("modalities"),
        )

        result = engine.personalize(request)

        return {
            "safety_cleared": result.safety_cleared,
            "matched_phenotype": result.matched_phenotype,
            "confidence_score": result.confidence_score,
            "confidence_band": result.confidence_band,
            "recommended_protocol": {
                "modality": result.recommended_protocol.modality,
                "target": result.recommended_protocol.target,
                "parameters": result.recommended_protocol.parameters,
                "evidence_level": result.recommended_protocol.evidence_level,
                "score": result.recommended_protocol.score,
                "rationale": result.recommended_protocol.rationale,
            } if result.recommended_protocol else None,
            "ranked_protocols_count": len(result.ranked_protocols),
            "blocked_modalities": result.blocked_modalities,
            "warnings": result.safety_warnings,
            "explanation": result.explanation,
        }

    # ── Serve React frontend (static files) ──────────────────────────
    # Must be LAST — catch-all for non-API routes serves index.html
    import os

    frontend_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if not frontend_dir.exists():
        # Try Fly.io build path
        frontend_dir = Path("/app/frontend/dist")

    if frontend_dir.exists():
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import FileResponse

        # Serve static assets (JS, CSS, images)
        assets_dir = frontend_dir / "assets"
        if assets_dir.exists():
            application.mount(
                "/assets",
                StaticFiles(directory=str(assets_dir)),
                name="frontend-assets",
            )

        # Serve other static files (favicon, etc.)
        @application.get("/favicon.ico")
        async def favicon():
            fav = frontend_dir / "favicon.ico"
            if fav.exists():
                return FileResponse(str(fav))
            return JSONResponse(status_code=404, content={})

        # SPA catch-all — any non-API route serves index.html
        @application.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            # Don't intercept API routes
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not found")
            # Try to serve actual file first
            file_path = frontend_dir / full_path
            if file_path.is_file():
                return FileResponse(str(file_path))
            # Otherwise serve index.html for client-side routing
            return FileResponse(str(frontend_dir / "index.html"))

        logger.info("Serving React frontend from %s", frontend_dir)
    else:
        logger.warning("Frontend dist not found at %s — SPA not served", frontend_dir)

    return application


# ── Module-level app instance (for uvicorn sozo_api.server:app) ───────────

app = create_app()
