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
from typing import Any

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

    return application


# ── Module-level app instance (for uvicorn sozo_api.server:app) ───────────

app = create_app()
