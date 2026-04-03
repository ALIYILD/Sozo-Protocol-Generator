"""
Visualization Service — wraps existing generators behind a uniform API.

Callers submit a VisualizationRequest, get back a VisualizationResponse
with rendered output + explanation + evidence + confidence.

Usage:
    from sozo_visuals.service import VisualizationService

    svc = VisualizationService()
    response = svc.render(VisualizationRequest(
        visual_type=VisualType.SPECTRAL_TOPOMAP,
        condition_slug="parkinsons",
    ))
"""
from __future__ import annotations

import logging
from typing import Optional

from .schemas import (
    RenderFormat,
    VisualEvidenceLink,
    VisualExplanation,
    VisualMetadata,
    VisualType,
    VisualizationRequest,
    VisualizationResponse,
)

logger = logging.getLogger(__name__)


class VisualizationService:
    """Unified visualization service wrapping all SOZO generators."""

    def __init__(self):
        self._renderers = {
            VisualType.SPECTRAL_TOPOMAP: self._render_spectral,
            VisualType.TARGET_OVERLAY: self._render_target_overlay,
            VisualType.NETWORK_HEXAGON: self._render_network_hexagon,
            VisualType.CONNECTIVITY_HEATMAP: self._render_connectivity,
            VisualType.BRAIN_MAP: self._render_brain_map,
            VisualType.MRI_TARGET: self._render_mri_target,
            VisualType.BEFORE_AFTER: self._render_before_after,
            VisualType.DOSE_RESPONSE: self._render_dose_response,
            VisualType.TREATMENT_TIMELINE: self._render_timeline,
        }

    def render(self, request: VisualizationRequest) -> VisualizationResponse:
        """Render a visualization from a structured request."""
        renderer = self._renderers.get(request.visual_type)
        if not renderer:
            return VisualizationResponse(
                visual_type=request.visual_type.value,
                error=f"Unsupported visual type: {request.visual_type.value}",
            )

        try:
            response = renderer(request)
            response.visual_type = request.visual_type.value
            response.render_format = request.render_format.value
            response.success = True

            # Attach metadata
            response.metadata.condition_slug = request.condition_slug
            response.metadata.protocol_id = request.protocol_id
            response.metadata.modality = request.modality
            response.metadata.source_generator = request.visual_type.value

            # Build explanation from knowledge if available
            if not response.explanation.summary:
                response.explanation = self._build_explanation(request)

            # Attach evidence from knowledge
            if not response.evidence:
                response.evidence = self._get_evidence(request)

            return response

        except Exception as e:
            logger.error(f"Render failed for {request.visual_type.value}: {e}", exc_info=True)
            return VisualizationResponse(
                visual_type=request.visual_type.value,
                error=str(e),
            )

    def list_types(self) -> list[str]:
        """List all supported visual types."""
        return [vt.value for vt in VisualType]

    # ── Renderer implementations ─────────────────────────────────────

    def _render_spectral(self, req: VisualizationRequest) -> VisualizationResponse:
        from sozo_generator.visuals.spectral_topomap import generate_spectral_topomap
        title = req.title or f"Spectral Band Profile — {req.condition_slug}"
        condition_name = self._resolve_condition_name(req.condition_slug)

        img_bytes = generate_spectral_topomap(
            title=title,
            condition_name=condition_name,
            spectral_data=req.spectral_data or None,
            dpi=req.dpi,
        )
        resp = VisualizationResponse(image_bytes=img_bytes, confidence=0.8)
        resp.metadata.bands = ["delta", "theta", "alpha", "beta", "gamma"]
        return resp

    def _render_target_overlay(self, req: VisualizationRequest) -> VisualizationResponse:
        from sozo_generator.visuals.qeeg_topomap import generate_qeeg_topomap
        title = req.title or f"Stimulation Target Map — {req.condition_slug}"
        condition_name = self._resolve_condition_name(req.condition_slug)

        img_bytes = generate_qeeg_topomap(
            title=title,
            condition_name=condition_name,
            anodes=req.anodes or None,
            cathodes=req.cathodes or None,
            tps_targets=req.tps_targets or None,
            intensity_map=req.intensity_map or None,
            subtitle=req.subtitle,
            dpi=req.dpi,
        )
        resp = VisualizationResponse(image_bytes=img_bytes, confidence=0.9)
        resp.metadata.targets = req.anodes + req.tps_targets
        return resp

    def _render_network_hexagon(self, req: VisualizationRequest) -> VisualizationResponse:
        from sozo_generator.visuals.connectivity_map import generate_connectivity_heatmap
        title = req.title or f"Network Connectivity — {req.condition_slug}"
        condition_name = self._resolve_condition_name(req.condition_slug)

        dysfunctions = req.network_dysfunctions
        if not dysfunctions:
            dysfunctions = self._load_network_dysfunctions(req.condition_slug)

        img_bytes = generate_connectivity_heatmap(
            title=title,
            condition_name=condition_name,
            network_dysfunctions=dysfunctions,
            dpi=req.dpi,
        )
        return VisualizationResponse(image_bytes=img_bytes, confidence=0.85)

    def _render_connectivity(self, req: VisualizationRequest) -> VisualizationResponse:
        return self._render_network_hexagon(req)

    def _render_brain_map(self, req: VisualizationRequest) -> VisualizationResponse:
        from sozo_generator.visuals.mri_target_view import generate_mri_target_view
        title = req.title or f"Stimulation Targets — {req.condition_slug}"
        condition_name = self._resolve_condition_name(req.condition_slug)

        targets = req.targets
        if not targets:
            targets = self._load_targets(req.condition_slug)

        img_bytes = generate_mri_target_view(
            title=title, condition_name=condition_name, targets=targets, dpi=req.dpi,
        )
        return VisualizationResponse(image_bytes=img_bytes, confidence=0.8)

    def _render_mri_target(self, req: VisualizationRequest) -> VisualizationResponse:
        return self._render_brain_map(req)

    def _render_before_after(self, req: VisualizationRequest) -> VisualizationResponse:
        """Render before/after comparison using two spectral topomaps."""
        from sozo_generator.visuals.spectral_topomap import generate_spectral_topomap
        condition_name = self._resolve_condition_name(req.condition_slug)

        # Generate baseline
        baseline_bytes = generate_spectral_topomap(
            title=f"Baseline — {condition_name}",
            condition_name=condition_name,
            spectral_data=req.baseline_features.get("spectral_data") if req.baseline_features else None,
            dpi=req.dpi,
        )
        # For MVP, return baseline visual with comparison metadata
        resp = VisualizationResponse(image_bytes=baseline_bytes, confidence=0.7)
        resp.metadata.comparison_type = "before_after"
        resp.metadata.timepoint = "baseline"
        resp.warnings.append("Full side-by-side comparison is Phase 2 — showing baseline view")
        return resp

    def _render_dose_response(self, req: VisualizationRequest) -> VisualizationResponse:
        from sozo_generator.visuals.dose_response import generate_dose_response
        condition_name = self._resolve_condition_name(req.condition_slug)
        img_bytes = generate_dose_response(
            title=req.title or "Response Tracking Template",
            condition_name=condition_name,
            dpi=req.dpi,
        )
        return VisualizationResponse(image_bytes=img_bytes, confidence=0.9)

    def _render_timeline(self, req: VisualizationRequest) -> VisualizationResponse:
        from sozo_generator.visuals.treatment_timeline import generate_treatment_timeline
        condition_name = self._resolve_condition_name(req.condition_slug)
        img_bytes = generate_treatment_timeline(
            title=req.title or "SOZO Session Timeline",
            condition_name=condition_name,
            phases=req.phases or None,
            dpi=req.dpi,
        )
        return VisualizationResponse(image_bytes=img_bytes, confidence=0.9)

    # ── Helpers ───────────────────────────────────────────────────────

    def _resolve_condition_name(self, slug: str) -> str:
        """Resolve condition slug to display name from knowledge."""
        try:
            from sozo_generator.knowledge.base import KnowledgeBase
            kb = KnowledgeBase()
            kb.load_all()
            cond = kb.get_condition(slug)
            if cond:
                return cond.display_name
        except Exception:
            pass
        return slug.replace("_", " ").title()

    def _load_network_dysfunctions(self, slug: str) -> dict:
        """Load network dysfunction profile from knowledge."""
        try:
            from sozo_generator.knowledge.base import KnowledgeBase
            kb = KnowledgeBase()
            kb.load_all()
            cond = kb.get_condition(slug)
            if cond:
                net_map = {"dmn": "DMN", "cen": "CEN", "sn": "SN",
                           "smn": "SMN", "limbic": "LIMBIC", "attention": "ATN"}
                return {
                    net_map.get(p.network, p.network.upper()): {
                        "dysfunction": p.dysfunction,
                        "severity": p.severity,
                        "involved": True,
                    }
                    for p in cond.network_profiles
                }
        except Exception:
            pass
        return {}

    def _load_targets(self, slug: str) -> list[dict]:
        """Load stimulation targets from knowledge for MRI view."""
        try:
            from sozo_generator.knowledge.base import KnowledgeBase
            kb = KnowledgeBase()
            kb.load_all()
            cond = kb.get_condition(slug)
            if cond:
                abbr_map = {
                    "L-DLPFC": "DLPFC", "R-DLPFC": "DLPFC", "M1": "M1",
                    "SMA": "SMA", "ACC": "ACC", "PPC": "PPC",
                    "Cerebellum": "Cerebellum", "OFC": "OFC",
                }
                targets = []
                seen = set()
                for p in cond.protocols:
                    region = abbr_map.get(p.target_abbreviation, p.target_abbreviation)
                    if region and region not in seen:
                        seen.add(region)
                        targets.append({"region": region, "modality": p.modality})
                return targets
        except Exception:
            pass
        return []

    def _build_explanation(self, req: VisualizationRequest) -> VisualExplanation:
        """Build clinician-facing explanation from context."""
        vtype = req.visual_type
        slug = req.condition_slug
        cond_name = self._resolve_condition_name(slug)

        explanations = {
            VisualType.SPECTRAL_TOPOMAP: VisualExplanation(
                summary=f"EEG spectral power distribution for {cond_name} across 5 frequency bands.",
                reasoning_chain=[
                    "Power spectral analysis computed per channel",
                    "Topographic interpolation across 10-10 electrode grid",
                    "Band-specific colormaps highlight condition-relevant patterns",
                ],
                network_interpretation="Spectral abnormalities map to network dysfunction profiles",
            ),
            VisualType.TARGET_OVERLAY: VisualExplanation(
                summary=f"Stimulation target placement for {cond_name} on the 10-10 EEG system.",
                reasoning_chain=[
                    "Targets derived from condition-specific protocol recommendations",
                    "Electrode positions follow international 10-10 standard",
                    "Anode/cathode/TPS targets color-coded for modality identification",
                ],
                protocol_link=f"Based on SOZO protocol recommendations for {cond_name}",
            ),
            VisualType.NETWORK_HEXAGON: VisualExplanation(
                summary=f"FNON network dysfunction profile for {cond_name}.",
                reasoning_chain=[
                    "6 functional brain networks evaluated",
                    "Dysfunction pattern (hypo/hyper) per network",
                    "Connectivity strength between network pairs",
                ],
                network_interpretation="FNON principle: stimulate dysfunctional networks, not symptoms",
            ),
            VisualType.BEFORE_AFTER: VisualExplanation(
                summary=f"Treatment response comparison for {cond_name}.",
                reasoning_chain=[
                    "Baseline vs follow-up feature comparison",
                    "Band power changes indicate treatment effect",
                ],
                confidence_note="Comparison quality depends on consistent recording conditions",
            ),
        }
        return explanations.get(vtype, VisualExplanation(summary=f"Visual for {cond_name}"))

    def _get_evidence(self, req: VisualizationRequest) -> list[VisualEvidenceLink]:
        """Get evidence links from knowledge for this condition."""
        try:
            from sozo_generator.knowledge.base import KnowledgeBase
            kb = KnowledgeBase()
            kb.load_all()
            cond = kb.get_condition(req.condition_slug)
            if cond:
                return [
                    VisualEvidenceLink(
                        pmid=ref.pmid or "",
                        claim=ref.title[:100],
                        relevance=f"Evidence for {cond.display_name} neuromodulation",
                    )
                    for ref in cond.references[:5]
                    if ref.pmid
                ]
        except Exception:
            pass
        return []
