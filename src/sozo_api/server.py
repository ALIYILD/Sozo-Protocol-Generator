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
from dataclasses import asdict
from typing import Any, Optional

# --- Conditional FastAPI import ---------------------------------------------------
# FastAPI may not be installed in all environments. The module remains valid Python
# regardless; callers get a clear ImportError with install instructions if missing.
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse, StreamingResponse
    from pydantic import BaseModel
except ImportError as _exc:
    raise ImportError(
        "FastAPI is required but not installed. "
        "Install it with:  pip install fastapi uvicorn"
    ) from _exc

logger = logging.getLogger(__name__)

# ── Pydantic request models (thin wrappers for non-schema endpoints) ──────

class CanonicalGenerateRequest(BaseModel):
    """Request body for POST /api/generate/canonical."""
    condition: str
    doc_type: str = "evidence_based_protocol"
    tier: str = "fellow"


class GraphGenerateRequest(BaseModel):
    """Request body for graph-based protocol generation."""
    condition_slug: str
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


# ── App factory ───────────────────────────────────────────────────────────

def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""

    application = FastAPI(
        title="SOZO Protocol API",
        version="1.0.0",
        description="HTTP interface for SOZO visualization, generation, knowledge, and cockpit services.",
    )

    # CORS — allow any frontend origin during development; tighten in prod.
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Router includes ──────────────────────────────────────────────
    from sozo_api.routes.protocols import router as protocols_router
    from sozo_api.routes.patients import router as patients_router
    from sozo_api.routes.reviews import router as reviews_router
    from sozo_api.routes.audit import router as audit_router

    try:
        from sozo_auth import auth_router
        application.include_router(auth_router, prefix="/api")
    except ImportError:
        logger.warning("sozo_auth not available — auth endpoints disabled")

    application.include_router(protocols_router)
    application.include_router(patients_router)
    application.include_router(reviews_router)
    application.include_router(audit_router)

    # ── Startup event ─────────────────────────────────────────────────

    @application.on_event("startup")
    async def _on_startup() -> None:
        logger.info("SOZO API started")
        # Auto-run Alembic migration on startup (SQLite safe)
        try:
            import os
            from pathlib import Path
            alembic_ini = Path(__file__).resolve().parents[2] / "alembic.ini"
            if alembic_ini.exists():
                from alembic.config import Config
                from alembic import command
                config = Config(str(alembic_ini))
                db_url = os.environ.get("DATABASE_URL", "sqlite:///sozo.db")
                sync_url = db_url.replace("+aiosqlite", "").replace("+asyncpg", "")
                config.set_main_option("sqlalchemy.url", sync_url)
                command.upgrade(config, "head")
                logger.info("Database migration complete")
        except Exception as exc:
            logger.warning("Auto-migration skipped: %s", exc)

    # ── Health ────────────────────────────────────────────────────────

    @application.get("/api/health")
    async def health() -> dict:
        return {"status": "ok"}

    # ── Visuals ───────────────────────────────────────────────────────

    @application.get("/api/visuals/types")
    async def list_visual_types() -> dict:
        """List all supported visualization types."""
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        return {"types": svc.list_types()}

    @application.post("/api/visuals/render")
    async def render_visual(request_body: dict[str, Any]) -> Any:
        """Render a visualization from a VisualizationRequest JSON body.

        Returns PNG bytes (as streaming response) when render_format is "png",
        or a JSON envelope with metadata, explanation, and evidence otherwise.
        """
        from sozo_visuals.schemas import VisualizationRequest, RenderFormat
        from sozo_visuals.service import VisualizationService

        try:
            req = VisualizationRequest(**request_body)
        except Exception as exc:
            raise HTTPException(status_code=422, detail=f"Invalid request: {exc}")

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

    # ── Generation ────────────────────────────────────────────────────

    @application.post("/api/generate/canonical")
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

    @application.get("/api/cockpit/overview")
    async def cockpit_overview() -> dict:
        """Platform-wide operational overview."""
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        ov = svc.overview()
        return {"overview": asdict(ov)}

    @application.get("/api/cockpit/conditions")
    async def cockpit_conditions() -> dict:
        """Per-condition operational summaries."""
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        summaries = svc.conditions_summary()
        return {"conditions": [asdict(s) for s in summaries]}

    # ── Shared graph checkpointer ────────────────────────────────────────

    _graph_checkpointer = None

    def _get_checkpointer():
        """Lazy-init a shared MemorySaver checkpointer.

        In production, replace with PostgresSaver for persistence across restarts.
        """
        nonlocal _graph_checkpointer
        if _graph_checkpointer is None:
            from langgraph.checkpoint.memory import MemorySaver
            _graph_checkpointer = MemorySaver()
        return _graph_checkpointer

    # ── Graph-based generation ─────────────────────────────────────────

    @application.post("/api/graph/generate")
    async def generate_via_graph(body: GraphGenerateRequest) -> dict:
        """Start a protocol generation pipeline via LangGraph.

        The pipeline runs through evidence search, safety checks, and
        composition, then pauses at the clinician review interrupt.

        Returns the thread_id needed to resume after review.
        """
        from sozo_graph.unified_graph import (
            build_unified_graph,
            create_initial_state,
        )

        try:
            effective_prompt = body.prompt or f"Generate {body.doc_type} for {body.condition_slug}"

            checkpointer = _get_checkpointer()
            graph = build_unified_graph(checkpointer=checkpointer)

            initial_state = create_initial_state(
                source_mode="prompt",
                user_prompt=effective_prompt,
                patient_context=body.patient_context,
                tier=body.tier,
            )

            thread_id = initial_state["request_id"]
            config = {"configurable": {"thread_id": thread_id}}

            # Run until clinician review interrupt
            result = graph.invoke(initial_state, config=config)

            # Persist GraphRun to database (non-blocking)
            try:
                from sozo_db.repositories.graph_run_repo import GraphRunRepository
                from sozo_db.engine import get_session_factory
                import asyncio

                async def _persist():
                    factory = get_session_factory()
                    async with factory() as session:
                        repo = GraphRunRepository(session)
                        await repo.create(result)
                        await session.commit()

                asyncio.get_event_loop().run_until_complete(_persist())
            except Exception as db_err:
                logger.warning("GraphRun DB persist skipped: %s", db_err)

            return {
                "success": True,
                "thread_id": thread_id,
                "status": result.get("status", "pending_review"),
                "condition": {
                    "slug": result.get("condition", {}).get("slug"),
                    "display_name": result.get("condition", {}).get("display_name"),
                    "valid": result.get("condition", {}).get("condition_valid"),
                },
                "evidence_summary": {
                    "total_articles": result.get("evidence", {}).get("screened_article_count", 0),
                    "sufficient": result.get("evidence", {}).get("evidence_sufficient", False),
                    "grade_distribution": result.get("evidence", {}).get("evidence_summary", {}).get("grade_distribution", {}),
                },
                "safety": {
                    "cleared": result.get("safety", {}).get("safety_cleared"),
                    "blocking": result.get("safety", {}).get("blocking_contraindications", []),
                    "off_label": result.get("safety", {}).get("off_label_flags", []),
                },
                "protocol": {
                    "sections_count": len(result.get("protocol", {}).get("composed_sections", [])),
                    "grounding_score": result.get("protocol", {}).get("grounding_score"),
                    "qa_passed": result.get("protocol", {}).get("qa_passed"),
                },
                "audit": {
                    "nodes_executed": len(result.get("node_history", [])),
                    "errors": len(result.get("errors", [])),
                },
            }
        except Exception as exc:
            logger.exception("Graph generation failed")
            raise HTTPException(status_code=500, detail=str(exc))

    @application.get("/api/graph/status/{thread_id}")
    async def graph_status(thread_id: str) -> dict:
        """Get the current status of a graph execution by thread_id.

        Returns the full review payload if the graph is paused at the
        clinician review interrupt.
        """
        from sozo_graph.unified_graph import build_unified_graph

        try:
            checkpointer = _get_checkpointer()
            graph = build_unified_graph(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}

            state = graph.get_state(config)
            if not state or not state.values:
                raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

            values = state.values
            review = values.get("review", {})
            evidence = values.get("evidence", {})
            safety = values.get("safety", {})
            protocol = values.get("protocol", {})

            return {
                "thread_id": thread_id,
                "status": values.get("status", "unknown"),
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
                        "node_id": n.get("node_id"),
                        "duration_ms": n.get("duration_ms"),
                        "status": n.get("status"),
                    }
                    for n in values.get("node_history", [])
                ],
                "output": values.get("output", {}),
            }

        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Graph status check failed")
            raise HTTPException(status_code=500, detail=str(exc))

    @application.post("/api/graph/review")
    async def submit_graph_review(body: GraphReviewRequest) -> dict:
        """Submit a clinician review decision and resume the graph.

        The graph will:
        - On approve: render output documents and write audit record
        - On reject: terminate (or re-compose if under max revisions)
        - On edit: apply edits and loop back to review
        """
        from sozo_graph.unified_graph import build_unified_graph
        from datetime import datetime, timezone

        try:
            checkpointer = _get_checkpointer()
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

            # Update state with review decision
            graph.update_state(config, {
                "review": {
                    "status": review_status,
                    "reviewer_id": body.reviewer_id,
                    "reviewer_credentials": body.reviewer_credentials,
                    "review_timestamp": now,
                    "review_notes": body.review_notes,
                    "revision_number": current_revision,
                    "edits_applied": body.section_edits or [],
                    "parameter_overrides": body.parameter_overrides or [],
                },
            })

            # Resume graph execution
            result = graph.invoke(None, config=config)

            return {
                "success": True,
                "thread_id": body.thread_id,
                "decision": body.decision,
                "status": result.get("status", "unknown"),
                "revision_number": result.get("review", {}).get("revision_number", 0),
                "output": result.get("output", {}),
                "audit_record_id": result.get("output", {}).get("audit_record_id"),
            }

        except HTTPException:
            raise
        except Exception as exc:
            logger.exception("Graph review submission failed")
            raise HTTPException(status_code=500, detail=str(exc))

    # Keep legacy endpoint as alias
    @application.post("/api/generate/graph")
    async def generate_via_graph_legacy(body: GraphGenerateRequest) -> dict:
        """Legacy alias for /api/graph/generate."""
        return await generate_via_graph(body)

    # ── Evidence staleness ─────────────────────────────────────────────

    @application.get("/api/evidence/staleness")
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

    @application.post("/api/safety/check")
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

    @application.post("/api/personalization/run")
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
    from pathlib import Path

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
