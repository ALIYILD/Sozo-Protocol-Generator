"""Tests for the new visual generators (QEEG, MRI, Protocol Panel, Connectivity)."""
import pytest
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from scipy.interpolate import Rbf
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@pytest.fixture(scope="module")
def parkinsons():
    from sozo_generator.conditions.generators.parkinsons import build_parkinsons_condition
    return build_parkinsons_condition()


@pytest.fixture(scope="module")
def output_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("visuals")


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestQEEGTopomap:
    def test_import(self):
        from sozo_generator.visuals.qeeg_topomap import (
            generate_qeeg_topomap,
            generate_qeeg_for_condition,
            EEG_10_10,
        )
        assert len(EEG_10_10) >= 64

    def test_generate_basic(self, output_dir):
        from sozo_generator.visuals.qeeg_topomap import generate_qeeg_topomap
        result = generate_qeeg_topomap(
            title="Test Protocol",
            condition_name="Test Condition",
            anodes=["C3", "C4"],
            cathodes=["Fp1", "Fp2"],
            output_path=str(output_dir / "test_qeeg.png"),
            show_heatmap=False,
        )
        assert len(result) > 10000  # PNG should be substantial
        assert (output_dir / "test_qeeg.png").exists()

    @pytest.mark.skipif(not HAS_SCIPY, reason="scipy not installed")
    def test_generate_with_heatmap(self, output_dir):
        from sozo_generator.visuals.qeeg_topomap import generate_qeeg_topomap
        result = generate_qeeg_topomap(
            title="Heatmap Test",
            condition_name="Test",
            anodes=["F3"],
            cathodes=["F4"],
            tps_targets=["Cz"],
            output_path=str(output_dir / "test_heatmap.png"),
            show_heatmap=True,
        )
        assert len(result) > 10000

    def test_generate_for_condition(self, parkinsons, output_dir):
        from sozo_generator.visuals.qeeg_topomap import generate_qeeg_for_condition
        path = generate_qeeg_for_condition(parkinsons, str(output_dir))
        if path:  # May be None if no targets map to electrodes
            assert path.exists()
            assert path.stat().st_size > 10000


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestMRITargetView:
    def test_import(self):
        from sozo_generator.visuals.mri_target_view import (
            generate_mri_target_view,
            generate_mri_for_condition,
            BRAIN_REGIONS,
        )
        assert len(BRAIN_REGIONS) >= 15

    def test_generate_basic(self, output_dir):
        from sozo_generator.visuals.mri_target_view import generate_mri_target_view
        result = generate_mri_target_view(
            title="Test MRI View",
            condition_name="Test",
            targets=[
                {"region": "DLPFC", "modality": "tdcs_anode", "intensity": 0.9},
                {"region": "M1", "modality": "tps", "intensity": 0.8},
            ],
            output_path=str(output_dir / "test_mri.png"),
        )
        assert len(result) > 10000
        assert (output_dir / "test_mri.png").exists()

    def test_generate_for_condition(self, parkinsons, output_dir):
        from sozo_generator.visuals.mri_target_view import generate_mri_for_condition
        path = generate_mri_for_condition(parkinsons, str(output_dir))
        if path:
            assert path.exists()
            assert path.stat().st_size > 10000


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestProtocolPanel:
    def test_import(self):
        from sozo_generator.visuals.protocol_panel import generate_protocol_panel

    def test_generate_basic(self, output_dir):
        from sozo_generator.visuals.protocol_panel import generate_protocol_panel
        result = generate_protocol_panel(
            title="Test Protocols",
            condition_name="Test",
            protocols=[
                {"code": "C1", "symptom": "Motor", "anodes": ["C3"], "cathodes": ["Fp1"], "tps_targets": []},
                {"code": "C2", "symptom": "Gait", "anodes": ["Fz"], "cathodes": ["Pz"], "tps_targets": []},
            ],
            output_path=str(output_dir / "test_panel.png"),
        )
        assert len(result) > 5000

    def test_generate_for_condition(self, parkinsons, output_dir):
        from sozo_generator.visuals.protocol_panel import generate_protocol_panel_for_condition
        paths = generate_protocol_panel_for_condition(parkinsons, str(output_dir))
        # Should generate TPS and tDCS panels
        assert len(paths) >= 1
        for p in paths:
            assert p.exists()


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestConnectivityMap:
    def test_import(self):
        from sozo_generator.visuals.connectivity_map import generate_connectivity_heatmap

    def test_generate_basic(self, output_dir):
        from sozo_generator.visuals.connectivity_map import generate_connectivity_heatmap
        result = generate_connectivity_heatmap(
            title="Test Connectivity",
            condition_name="Test",
            network_dysfunctions={
                "DMN": {"dysfunction": "hyper", "severity": "severe", "involved": True},
                "CEN": {"dysfunction": "hypo", "severity": "moderate", "involved": True},
                "SN": {"dysfunction": "hyper", "severity": "high", "involved": True},
            },
            output_path=str(output_dir / "test_connectivity.png"),
        )
        assert len(result) > 10000

    def test_generate_for_condition(self, parkinsons, output_dir):
        from sozo_generator.visuals.connectivity_map import generate_connectivity_for_condition
        path = generate_connectivity_for_condition(parkinsons, str(output_dir))
        if path:
            assert path.exists()
            assert path.stat().st_size > 10000


@pytest.mark.skipif(not HAS_MATPLOTLIB, reason="matplotlib not installed")
class TestGenerationServiceVisuals:
    """Test that GenerationService correctly routes to new visual generators."""

    def test_visual_generators_loaded(self):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService()
        generators = svc._get_visual_generators()
        assert "qeeg_topomap" in generators
        assert "mri_target_view" in generators
        assert "montage_panel" in generators
        assert "connectivity_map" in generators

    def test_generate_with_visuals(self, parkinsons):
        from sozo_generator.generation.service import GenerationService
        svc = GenerationService(with_visuals=True, with_qa=False)
        results = svc.generate(
            condition="parkinsons",
            tier="fellow",
            doc_type="evidence_based_protocol",
            with_visuals=True,
        )
        assert results[0].success
        # Should have generated some visuals
        assert len(results[0].visuals_generated) >= 1
