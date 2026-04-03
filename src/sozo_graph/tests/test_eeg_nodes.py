"""Tests for EEG personalization subgraph nodes."""
import pytest


class TestEEGFeatureLoader:
    def test_skips_when_no_eeg(self):
        from sozo_graph.nodes.eeg_feature_loader import eeg_feature_loader

        state = {"eeg": {"data_available": False}}
        result = eeg_feature_loader(state)
        assert result["eeg"]["data_available"] is False

    def test_uses_precomputed_features(self):
        from sozo_graph.nodes.eeg_feature_loader import eeg_feature_loader

        state = {
            "eeg": {
                "data_available": True,
                "features": {
                    "alpha_power_f3": 12.5,
                    "alpha_power_f4": 14.2,
                    "theta_beta_ratio": 3.8,
                    "frontal_alpha_asymmetry": -0.15,
                    "beta_power_c3": 18.0,
                },
            },
        }
        result = eeg_feature_loader(state)
        assert result["eeg"]["data_available"] is True
        assert result["eeg"]["quality_metrics"]["usable"] is True
        assert "alpha" in result["eeg"]["quality_metrics"]["bands_present"]

    def test_quality_warns_on_missing_bands(self):
        from sozo_graph.nodes.eeg_feature_loader import eeg_feature_loader

        state = {
            "eeg": {
                "data_available": True,
                "features": {"some_metric": 5.0},
            },
        }
        result = eeg_feature_loader(state)
        quality = result["eeg"]["quality_metrics"]
        assert len(quality["warnings"]) > 0


class TestEEGInterpreter:
    def test_rule_based_depression(self):
        from sozo_graph.nodes.eeg_interpreter import _rule_based_interpret

        features = {
            "frontal_alpha_asymmetry": -0.2,
            "theta_beta_ratio": 3.5,
        }
        condition = {"slug": "depression", "display_name": "Depression"}
        evidence = {"articles": []}

        result = _rule_based_interpret(features, condition, evidence)
        assert len(result.primary_findings) >= 1
        assert any("alpha" in f.biomarker.lower() for f in result.primary_findings)

    def test_rule_based_parkinsons(self):
        from sozo_graph.nodes.eeg_interpreter import _rule_based_interpret

        features = {"beta_power_c3": 20.0}
        condition = {"slug": "parkinsons", "display_name": "Parkinson's Disease"}
        evidence = {"articles": []}

        result = _rule_based_interpret(features, condition, evidence)
        assert len(result.primary_findings) >= 1
        assert any("beta" in f.biomarker.lower() for f in result.primary_findings)

    def test_no_findings_for_unrelated(self):
        from sozo_graph.nodes.eeg_interpreter import _rule_based_interpret

        features = {"some_feature": 5.0}
        condition = {"slug": "tinnitus", "display_name": "Tinnitus"}
        evidence = {"articles": []}

        result = _rule_based_interpret(features, condition, evidence)
        assert result.confidence in ("low", "insufficient")


class TestEEGPersonalizer:
    def test_applies_valid_adjustment(self):
        from sozo_graph.nodes.eeg_personalizer import eeg_personalizer

        state = {
            "eeg": {
                "data_available": True,
                "interpretation": {
                    "recommended_adjustments": [
                        {
                            "parameter": "target",
                            "current_value": "left DLPFC",
                            "recommended_value": "left DLPFC (confirmed by EEG)",
                            "rationale": "Alpha asymmetry confirms left hypoactivation",
                            "confidence": "medium",
                        },
                    ],
                },
            },
            "protocol": {
                "base_sequence": {
                    "sequence_id": "seq-001",
                    "all_modalities": ["tdcs"],
                },
            },
        }
        result = eeg_personalizer(state)
        assert len(result["eeg"]["adjustments_applied"]) == 1
        assert len(result["eeg"]["adjustments_rejected"]) == 0

    def test_rejects_unsafe_intensity(self):
        from sozo_graph.nodes.eeg_personalizer import eeg_personalizer

        state = {
            "eeg": {
                "data_available": True,
                "interpretation": {
                    "recommended_adjustments": [
                        {
                            "parameter": "intensity_ma",
                            "current_value": "2.0",
                            "recommended_value": "5.0",  # exceeds tDCS max of 2.0
                            "rationale": "Higher intensity might help",
                            "confidence": "medium",
                        },
                    ],
                },
            },
            "protocol": {
                "base_sequence": {
                    "sequence_id": "seq-001",
                    "all_modalities": ["tdcs"],
                },
            },
        }
        result = eeg_personalizer(state)
        assert len(result["eeg"]["adjustments_applied"]) == 0
        assert len(result["eeg"]["adjustments_rejected"]) == 1
        assert "above max" in result["eeg"]["adjustments_rejected"][0]["rejection_reason"].lower()

    def test_rejects_low_confidence_with_uncertainty(self):
        from sozo_graph.nodes.eeg_personalizer import eeg_personalizer

        state = {
            "eeg": {
                "data_available": True,
                "interpretation": {
                    "recommended_adjustments": [
                        {
                            "parameter": "frequency_hz",
                            "current_value": "10",
                            "recommended_value": "15",
                            "rationale": "Maybe higher frequency",
                            "confidence": "low",
                            "uncertainty_flag": "Very limited evidence for this adjustment",
                        },
                    ],
                },
            },
            "protocol": {
                "base_sequence": {
                    "sequence_id": "seq-001",
                    "all_modalities": ["tavns"],
                },
            },
        }
        result = eeg_personalizer(state)
        assert len(result["eeg"]["adjustments_rejected"]) == 1

    def test_no_adjustments_passes_through(self):
        from sozo_graph.nodes.eeg_personalizer import eeg_personalizer

        state = {
            "eeg": {
                "data_available": True,
                "interpretation": {"recommended_adjustments": []},
            },
            "protocol": {"base_sequence": {}},
        }
        result = eeg_personalizer(state)
        assert result["eeg"]["adjustments_applied"] == []


class TestEEGGraphRouting:
    def test_graph_compiles_with_eeg_nodes(self):
        from sozo_graph.graph import build_sozo_graph
        from langgraph.checkpoint.memory import MemorySaver

        graph = build_sozo_graph(checkpointer=MemorySaver())
        nodes = list(graph.get_graph().nodes.keys())

        assert "eeg_feature_loader" in nodes
        assert "eeg_interpreter" in nodes
        assert "eeg_personalizer" in nodes
