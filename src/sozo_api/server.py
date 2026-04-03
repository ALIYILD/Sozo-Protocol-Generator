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

    # ── Graph-based generation ─────────────────────────────────────────

    @application.post("/api/generate/graph")
    async def generate_via_graph(body: GraphGenerateRequest) -> dict:
        """Generate a protocol using the unified LangGraph pipeline.

        This is the production generation path that runs:
        intake -> condition -> evidence -> safety -> personalization ->
        composition -> grounding -> QA -> [review interrupt] -> render
        """
        from sozo_graph.unified_graph import (
            build_unified_graph,
            create_initial_state,
            run_unified_generation,
        )

        try:
            # Build prompt from condition_slug and optional user prompt
            effective_prompt = body.prompt or f"Generate {body.doc_type} for {body.condition_slug}"

            result = run_unified_generation(
                user_prompt=effective_prompt,
                tier=body.tier,
            )

            return {
                "success": True,
                "status": result.get("review", {}).get("status", "pending_review"),
                "protocol": result.get("protocol", {}),
                "evidence_summary": {
                    "total_articles": result.get("evidence", {}).get("total_articles", 0),
                    "sufficiency": result.get("evidence", {}).get("evidence_sufficient", False),
                },
                "safety": result.get("safety", {}),
                "qa_summary": result.get("protocol", {}).get("qa_summary", {}),
                "output": result.get("output", {}),
                "audit": {
                    "node_count": len(result.get("node_history", [])),
                    "errors": len(result.get("errors", [])),
                },
            }
        except Exception as exc:
            logger.exception("Graph generation failed")
            raise HTTPException(status_code=500, detail=str(exc))

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

    return application


# ── Module-level app instance (for uvicorn sozo_api.server:app) ───────────

app = create_app()
