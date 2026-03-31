"""Tests for visual generation. Skips gracefully if matplotlib unavailable."""
import pytest

pytest.importorskip("matplotlib", reason="matplotlib not installed")


pytestmark = pytest.mark.slow


@pytest.mark.slow
def test_brain_map_generates(parkinsons_condition, tmp_output):
    """BrainMapGenerator.generate_target_map returns a Path and the file exists."""
    from sozo_generator.visuals.brain_maps import BrainMapGenerator
    from pathlib import Path

    output_dir = tmp_output / "brain_maps"
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = BrainMapGenerator()
    result = generator.generate_target_map(parkinsons_condition, output_dir)

    assert result is not None, "generate_target_map returned None"
    assert isinstance(result, Path), f"Expected Path, got {type(result)}"
    assert result.exists(), f"Brain map file not found: {result}"


@pytest.mark.slow
def test_network_diagram_generates(parkinsons_condition, tmp_output):
    """NetworkDiagramGenerator.generate_network_diagram returns a Path and the file exists."""
    from sozo_generator.visuals.network_diagrams import NetworkDiagramGenerator
    from pathlib import Path

    output_dir = tmp_output / "network_diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = NetworkDiagramGenerator()
    result = generator.generate_network_diagram(parkinsons_condition, output_dir)

    assert result is not None, "generate_network_diagram returned None"
    assert isinstance(result, Path), f"Expected Path, got {type(result)}"
    assert result.exists(), f"Network diagram file not found: {result}"


@pytest.mark.slow
def test_patient_journey_generates(tmp_output):
    """PatientJourneyGenerator.generate_journey_diagram returns a Path and file exists."""
    from sozo_generator.visuals.patient_journey import PatientJourneyGenerator
    from pathlib import Path

    output_dir = tmp_output / "patient_journey"
    output_dir.mkdir(parents=True, exist_ok=True)

    generator = PatientJourneyGenerator()
    result = generator.generate_journey_diagram("parkinsons", output_dir)

    assert result is not None, "generate_journey_diagram returned None"
    assert isinstance(result, Path), f"Expected Path, got {type(result)}"
    assert result.exists(), f"Patient journey file not found: {result}"


@pytest.mark.slow
def test_exporter_generate_all(parkinsons_condition, tmp_output):
    """VisualsExporter.generate_all returns a dict with 4 keys, all non-None."""
    from sozo_generator.visuals.exporters import VisualsExporter

    output_dir = tmp_output / "visuals_exporter"
    output_dir.mkdir(parents=True, exist_ok=True)

    exporter = VisualsExporter(output_dir)
    results = exporter.generate_all(parkinsons_condition, force=True)

    assert isinstance(results, dict), f"Expected dict, got {type(results)}"
    assert len(results) == 4, f"Expected 4 keys in results, got {len(results)}: {list(results.keys())}"

    expected_keys = {"brain_map", "network_diagram", "symptom_flow", "patient_journey"}
    assert set(results.keys()) == expected_keys, (
        f"Unexpected result keys: {set(results.keys())}"
    )

    for key, value in results.items():
        assert value is not None, f"Visual '{key}' returned None"
