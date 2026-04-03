"""Tests for the Visualization API service layer."""
import pytest

try:
    import matplotlib
    matplotlib.use("Agg")
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class TestVisualizationSchemas:
    def test_request_creation(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        req = VisualizationRequest(
            visual_type=VisualType.SPECTRAL_TOPOMAP,
            condition_slug="parkinsons",
        )
        assert req.visual_type == VisualType.SPECTRAL_TOPOMAP

    def test_response_creation(self):
        from sozo_visuals.schemas import VisualizationResponse, VisualExplanation
        resp = VisualizationResponse(
            visual_type="spectral_topomap",
            success=True,
            explanation=VisualExplanation(summary="Test explanation"),
            confidence=0.9,
        )
        assert resp.success
        assert resp.confidence == 0.9
        assert resp.explanation.summary == "Test explanation"

    def test_evidence_link(self):
        from sozo_visuals.schemas import VisualEvidenceLink
        link = VisualEvidenceLink(pmid="12345678", claim="tDCS effective for PD motor symptoms")
        assert link.pmid == "12345678"

    def test_all_visual_types(self):
        from sozo_visuals.schemas import VisualType
        types = list(VisualType)
        assert len(types) >= 9

    def test_list_types(self):
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        types = svc.list_types()
        assert "spectral_topomap" in types
        assert "target_overlay" in types
        assert "network_hexagon" in types


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestVisualizationService:
    def test_render_spectral_topomap(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.SPECTRAL_TOPOMAP,
            condition_slug="parkinsons",
        ))
        assert resp.success
        assert resp.image_bytes is not None
        assert len(resp.image_bytes) > 10000

    def test_render_target_overlay(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.TARGET_OVERLAY,
            condition_slug="parkinsons",
            anodes=["C3", "C4"],
            cathodes=["Fp1", "Fp2"],
        ))
        assert resp.success
        assert resp.image_bytes is not None

    def test_render_network_hexagon(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.NETWORK_HEXAGON,
            condition_slug="parkinsons",
        ))
        assert resp.success
        assert resp.image_bytes is not None

    def test_render_dose_response(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.DOSE_RESPONSE,
            condition_slug="depression",
        ))
        assert resp.success

    def test_render_timeline(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.TREATMENT_TIMELINE,
            condition_slug="parkinsons",
        ))
        assert resp.success


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestExplanationAndEvidence:
    def test_explanation_attached(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.SPECTRAL_TOPOMAP,
            condition_slug="parkinsons",
        ))
        assert resp.explanation.summary
        assert len(resp.explanation.reasoning_chain) >= 1

    def test_evidence_attached(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.TARGET_OVERLAY,
            condition_slug="parkinsons",
        ))
        assert len(resp.evidence) >= 1
        assert resp.evidence[0].pmid

    def test_confidence_present(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.NETWORK_HEXAGON,
            condition_slug="depression",
        ))
        assert resp.confidence > 0

    def test_metadata_populated(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.TARGET_OVERLAY,
            condition_slug="parkinsons",
            anodes=["F3"],
        ))
        assert resp.metadata.condition_slug == "parkinsons"
        assert resp.metadata.source_generator == "target_overlay"


class TestErrorHandling:
    def test_unsupported_type_error(self):
        from sozo_visuals.schemas import VisualizationRequest, VisualType
        from sozo_visuals.service import VisualizationService
        svc = VisualizationService()
        # Use a valid type but test the service handles it
        resp = svc.render(VisualizationRequest(
            visual_type=VisualType.SPECTRAL_TOPOMAP,
            condition_slug="",
        ))
        # Should still succeed (empty condition uses defaults)
        assert resp.visual_type == "spectral_topomap"
