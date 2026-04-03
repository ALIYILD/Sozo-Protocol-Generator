"""Comprehensive tests for ALL 10 visual generators."""
import pytest
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


@pytest.fixture(scope="module")
def parkinsons():
    from sozo_generator.conditions.generators.parkinsons import build_parkinsons_condition
    return build_parkinsons_condition()


@pytest.fixture(scope="module")
def depression():
    from sozo_generator.conditions.generators.depression import build_depression_condition
    return build_depression_condition()


@pytest.fixture(scope="module")
def out(tmp_path_factory):
    return tmp_path_factory.mktemp("all_visuals")


# ── Existing generators (quick check) ──────────────────────────────────────


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestExistingVisuals:
    def test_qeeg_topomap(self, parkinsons, out):
        from sozo_generator.visuals.qeeg_topomap import generate_qeeg_for_condition
        p = generate_qeeg_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 5000

    def test_mri_target_view(self, parkinsons, out):
        from sozo_generator.visuals.mri_target_view import generate_mri_for_condition
        p = generate_mri_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 5000

    def test_protocol_panel(self, parkinsons, out):
        from sozo_generator.visuals.protocol_panel import generate_protocol_panel_for_condition
        paths = generate_protocol_panel_for_condition(parkinsons, str(out))
        assert len(paths) >= 1
        for p in paths:
            assert p.exists() and p.stat().st_size > 5000

    def test_connectivity_map(self, parkinsons, out):
        from sozo_generator.visuals.connectivity_map import generate_connectivity_for_condition
        p = generate_connectivity_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 5000


# ── New generators ─────────────────────────────────────────────────────────


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestAxialBrainView:
    def test_generates_for_parkinsons(self, parkinsons, out):
        from sozo_generator.visuals.axial_brain_view import generate_axial_for_condition
        p = generate_axial_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 10000

    def test_generates_for_depression(self, depression, out):
        from sozo_generator.visuals.axial_brain_view import generate_axial_for_condition
        p = generate_axial_for_condition(depression, str(out))
        assert p and p.exists()

    def test_low_level_api(self, out):
        from sozo_generator.visuals.axial_brain_view import generate_axial_brain_view
        result = generate_axial_brain_view(
            title="Test Axial",
            condition_name="Test",
            targets=[{"region": "L-DLPFC", "modality": "tdcs_anode"}],
            output_path=str(out / "test_axial.png"),
        )
        assert len(result) > 5000


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestCoronalBrainView:
    def test_generates_for_parkinsons(self, parkinsons, out):
        from sozo_generator.visuals.coronal_brain_view import generate_coronal_for_condition
        p = generate_coronal_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 10000

    def test_low_level_api(self, out):
        from sozo_generator.visuals.coronal_brain_view import generate_coronal_brain_view
        result = generate_coronal_brain_view(
            title="Test Coronal",
            condition_name="Test",
            targets=[
                {"region": "DLPFC", "modality": "tdcs_anode"},
                {"region": "Thalamus", "modality": "tps"},
            ],
            output_path=str(out / "test_coronal.png"),
        )
        assert len(result) > 5000


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestTreatmentTimeline:
    def test_generates_for_parkinsons(self, parkinsons, out):
        from sozo_generator.visuals.treatment_timeline import generate_timeline_for_condition
        p = generate_timeline_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 5000

    def test_default_phases(self, out):
        from sozo_generator.visuals.treatment_timeline import generate_treatment_timeline
        result = generate_treatment_timeline(
            title="Default SOZO Session",
            condition_name="Test",
            output_path=str(out / "test_timeline.png"),
        )
        assert len(result) > 5000

    def test_custom_phases(self, out):
        from sozo_generator.visuals.treatment_timeline import generate_treatment_timeline
        result = generate_treatment_timeline(
            title="Custom Timeline",
            condition_name="Test",
            phases=[
                {"label": "Phase A", "device": "tDCS", "start_min": 0,
                 "duration_min": 20, "color": "#2E75B6", "description": "Priming"},
                {"label": "Phase B", "device": "TPS", "start_min": 20,
                 "duration_min": 30, "color": "#E07B39", "description": "Targeting"},
            ],
            output_path=str(out / "test_custom_timeline.png"),
        )
        assert len(result) > 5000


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestDoseResponse:
    def test_generates_for_parkinsons(self, parkinsons, out):
        from sozo_generator.visuals.dose_response import generate_dose_response_for_condition
        p = generate_dose_response_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 5000

    def test_default_template(self, out):
        from sozo_generator.visuals.dose_response import generate_dose_response
        result = generate_dose_response(
            title="Response Tracking",
            condition_name="Test Condition",
            primary_outcome="PHQ-9",
            output_path=str(out / "test_dose.png"),
        )
        assert len(result) > 5000


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestSpectralTopomap:
    def test_generates_for_parkinsons(self, parkinsons, out):
        from sozo_generator.visuals.spectral_topomap import generate_spectral_for_condition
        p = generate_spectral_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 10000

    def test_generates_for_depression(self, depression, out):
        from sozo_generator.visuals.spectral_topomap import generate_spectral_for_condition
        p = generate_spectral_for_condition(depression, str(out))
        assert p and p.exists()


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestImpedanceMap:
    def test_generates_for_parkinsons(self, parkinsons, out):
        from sozo_generator.visuals.impedance_map import generate_impedance_for_condition
        p = generate_impedance_for_condition(parkinsons, str(out))
        assert p and p.exists() and p.stat().st_size > 5000

    def test_template_mode(self, out):
        from sozo_generator.visuals.impedance_map import generate_impedance_map
        result = generate_impedance_map(
            title="Impedance Check",
            condition_name="Test",
            output_path=str(out / "test_impedance.png"),
        )
        assert len(result) > 5000


# ── Integration: GenerationService visual registry ─────────────────────────


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestVisualRegistry:
    def test_all_generators_registered(self):
        from sozo_generator.generation.service import GenerationService
        gens = GenerationService._get_visual_generators()
        expected = [
            "brain_map", "network_diagram", "qeeg_topomap", "eeg_topomap",
            "mri_target_view", "montage_panel", "protocol_panel",
            "connectivity_map", "symptom_flow", "patient_journey",
            "axial_brain_view", "coronal_brain_view",
            "treatment_timeline", "dose_response",
            "spectral_topomap", "impedance_map",
        ]
        for name in expected:
            assert name in gens, f"Missing visual generator: {name}"

    def test_total_generator_count(self):
        from sozo_generator.generation.service import GenerationService
        gens = GenerationService._get_visual_generators()
        # At least 16 entries (some are aliases like eeg_topomap -> qeeg_topomap)
        assert len(gens) >= 16


# ── Full pipeline: generate with all visuals ───────────────────────────────


@pytest.mark.skipif(not HAS_MPL, reason="matplotlib not installed")
class TestFullVisualPipeline:
    def test_evidence_protocol_generates_all_visuals(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=True, with_qa=False)
        results = svc.generate(
            condition="parkinsons",
            tier="fellow",
            doc_type="evidence_based_protocol",
        )
        assert results[0].success
        # Evidence-Based Protocol has 9 visual specs now
        assert len(results[0].visuals_generated) >= 5, (
            f"Expected >=5 visuals, got {len(results[0].visuals_generated)}: "
            f"{results[0].visuals_generated}"
        )

    def test_all_in_one_generates_visuals(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=True, with_qa=False)
        results = svc.generate(
            condition="parkinsons",
            tier="fellow",
            doc_type="all_in_one_protocol",
        )
        assert results[0].success
        assert len(results[0].visuals_generated) >= 3
