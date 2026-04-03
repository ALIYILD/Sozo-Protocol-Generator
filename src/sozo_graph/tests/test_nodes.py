"""
Tests for individual Sozo graph nodes.

Tests verify:
- Node functions accept state dicts and return partial updates
- Audit decorator captures history entries
- Safety gates block when they should
- Deterministic nodes produce consistent output
"""
import pytest


class TestIntakeRouter:
    def test_routes_prompt(self):
        from sozo_graph.nodes.intake_router import intake_router

        state = {
            "intake": {"user_prompt": "Generate tDCS protocol for depression"},
            "source_mode": "",
        }
        result = intake_router(state)
        assert result["source_mode"] == "prompt"
        assert len(result["node_history"]) == 1
        assert result["node_history"][0]["node_id"] == "intake_router"
        assert result["node_history"][0]["status"] == "success"

    def test_routes_upload(self):
        from sozo_graph.nodes.intake_router import intake_router

        state = {
            "intake": {"uploaded_filename": "protocol.docx"},
            "source_mode": "",
        }
        result = intake_router(state)
        assert result["source_mode"] == "upload"

    def test_defaults_to_prompt(self):
        from sozo_graph.nodes.intake_router import intake_router

        state = {"intake": {}, "source_mode": ""}
        result = intake_router(state)
        assert result["source_mode"] == "prompt"


class TestPromptNormalizer:
    def test_keyword_fallback_depression(self):
        from sozo_graph.nodes.prompt_normalizer import _keyword_normalize

        result = _keyword_normalize("Generate a tDCS protocol for depression")
        assert result.condition_slug == "depression"
        assert "tdcs" in result.modality_preferences

    def test_keyword_fallback_parkinsons(self):
        from sozo_graph.nodes.prompt_normalizer import _keyword_normalize

        result = _keyword_normalize("Parkinson's disease treatment protocol with TPS")
        assert result.condition_slug == "parkinsons"
        assert "tps" in result.modality_preferences

    def test_keyword_fallback_unknown(self):
        from sozo_graph.nodes.prompt_normalizer import _keyword_normalize

        result = _keyword_normalize("Something completely unrelated")
        assert result.condition_slug == ""
        assert len(result.uncertainty_flags) > 0

    def test_eeg_detection(self):
        from sozo_graph.nodes.prompt_normalizer import _keyword_normalize

        result = _keyword_normalize("Depression protocol with QEEG data available")
        assert result.eeg_data_referenced is True


class TestConditionResolver:
    def test_resolves_valid_condition(self):
        from sozo_graph.nodes.condition_resolver import condition_resolver

        state = {
            "intake": {
                "normalized_request": {"condition_slug": "parkinsons"},
            },
            "condition": {},
        }
        result = condition_resolver(state)
        condition = result.get("condition", {})
        assert condition.get("condition_valid") is True
        assert condition.get("slug") == "parkinsons"
        assert condition.get("display_name") == "Parkinson's Disease"
        assert condition.get("icd10") == "G20"

    def test_rejects_invalid_condition(self):
        from sozo_graph.nodes.condition_resolver import condition_resolver

        state = {
            "intake": {
                "normalized_request": {"condition_slug": "nonexistent_condition"},
            },
            "condition": {},
        }
        result = condition_resolver(state)
        assert result["condition"]["condition_valid"] is False


class TestEvidenceSufficiencyGate:
    def test_passes_with_sufficient_evidence(self):
        from sozo_graph.nodes.evidence_sufficiency_gate import evidence_sufficiency_gate

        state = {
            "evidence": {
                "evidence_sufficient": True,
                "evidence_summary": {
                    "grade_distribution": {"A": 3, "B": 5, "C": 2, "D": 1},
                    "total_articles": 11,
                },
                "evidence_gaps": [],
            },
        }
        result = evidence_sufficiency_gate(state)
        assert result["evidence"]["evidence_sufficient"] is True

    def test_flags_insufficient_evidence(self):
        from sozo_graph.nodes.evidence_sufficiency_gate import evidence_sufficiency_gate

        state = {
            "evidence": {
                "evidence_sufficient": False,
                "evidence_summary": {
                    "grade_distribution": {"C": 1, "D": 2},
                    "total_articles": 3,
                },
                "evidence_gaps": [],
            },
        }
        result = evidence_sufficiency_gate(state)
        assert result["evidence"]["evidence_sufficient"] is False
        assert len(result["evidence"]["evidence_gaps"]) > 0


class TestSafetyPolicyEngine:
    def test_clears_safe_patient(self):
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine

        state = {
            "condition": {
                "slug": "depression",
                "schema_dict": {
                    "stimulation_targets": [{"modality": "tdcs"}],
                },
            },
            "patient_context": {
                "contraindications": [],
                "current_medications": [],
            },
        }
        result = safety_policy_engine(state)
        assert result["safety"]["safety_cleared"] is True

    def test_blocks_contraindicated_patient(self):
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine

        state = {
            "condition": {
                "slug": "depression",
                "schema_dict": {
                    "stimulation_targets": [{"modality": "tdcs"}],
                },
            },
            "patient_context": {
                "contraindications": ["metallic_cranial_implant"],
                "current_medications": [],
            },
        }
        result = safety_policy_engine(state)
        assert result["safety"]["safety_cleared"] is False
        assert len(result["safety"]["blocking_contraindications"]) > 0

    def test_flags_off_label_tps(self):
        from sozo_graph.nodes.safety_policy_engine import safety_policy_engine

        state = {
            "condition": {
                "slug": "depression",  # TPS not approved for depression
                "schema_dict": {
                    "stimulation_targets": [{"modality": "tps"}],
                },
            },
            "patient_context": {
                "contraindications": [],
                "current_medications": [],
            },
        }
        result = safety_policy_engine(state)
        assert len(result["safety"]["off_label_flags"]) > 0
        assert any("off-label" in f.lower() for f in result["safety"]["off_label_flags"])


class TestContraindicationGate:
    def test_passes_when_cleared(self):
        from sozo_graph.nodes.contraindication_gate import contraindication_gate

        state = {"safety": {"safety_cleared": True, "blocking_contraindications": []}}
        result = contraindication_gate(state)
        assert result.get("status") != "error"

    def test_blocks_when_contraindicated(self):
        from sozo_graph.nodes.contraindication_gate import contraindication_gate

        state = {
            "safety": {
                "safety_cleared": False,
                "blocking_contraindications": ["tdcs: metallic_cranial_implant"],
            },
        }
        result = contraindication_gate(state)
        assert result["status"] == "error"


class TestGroundingValidator:
    def test_validates_good_citations(self):
        from sozo_graph.nodes.grounding_validator import grounding_validator

        state = {
            "evidence": {
                "articles": [
                    {"pmid": "12345678", "doi": None, "title": "Study A"},
                    {"pmid": "87654321", "doi": None, "title": "Study B"},
                ],
            },
            "condition": {"slug": "depression"},
            "protocol": {
                "composed_sections": [
                    {
                        "section_id": "overview",
                        "title": "Overview",
                        "content": "tDCS shows promise for depression.",
                        "cited_evidence_ids": ["12345678"],
                        "claims": [
                            {
                                "claim_text": "tDCS shows promise",
                                "evidence_ids": ["12345678"],
                                "claim_type": "supports",
                                "confidence": "high",
                            }
                        ],
                    }
                ],
            },
        }
        result = grounding_validator(state)
        assert result["protocol"]["grounding_score"] == 1.0

    def test_flags_unverified_citations(self):
        from sozo_graph.nodes.grounding_validator import grounding_validator

        state = {
            "evidence": {"articles": []},  # no articles
            "condition": {"slug": "test"},
            "protocol": {
                "composed_sections": [
                    {
                        "section_id": "test",
                        "title": "Test",
                        "content": "Some claim.",
                        "cited_evidence_ids": ["99999999"],
                        "claims": [],
                    }
                ],
            },
        }
        result = grounding_validator(state)
        assert result["protocol"]["grounding_score"] == 0.0
        assert len(result["protocol"]["grounding_issues"]) > 0


class TestReviewProcessor:
    def test_approve(self):
        from sozo_graph.nodes.review_processor import review_processor

        state = {
            "review": {
                "status": "approved",
                "reviewer_id": "dr_smith",
                "revision_number": 0,
            },
            "protocol": {"composed_sections": []},
        }
        result = review_processor(state)
        assert result["status"] == "approved"
        assert result["review"]["approval_stamp"]["reviewer_id"] == "dr_smith"

    def test_reject(self):
        from sozo_graph.nodes.review_processor import review_processor

        state = {
            "review": {
                "status": "rejected",
                "reviewer_id": "dr_smith",
                "review_notes": "Evidence too weak",
                "revision_number": 0,
            },
            "protocol": {"composed_sections": []},
        }
        result = review_processor(state)
        assert result["status"] == "rejected"


class TestAuditDecorator:
    def test_captures_history(self):
        from sozo_graph.nodes.intake_router import intake_router

        state = {"intake": {"user_prompt": "test"}, "source_mode": ""}
        result = intake_router(state)

        assert "node_history" in result
        assert len(result["node_history"]) == 1
        entry = result["node_history"][0]
        assert entry["node_id"] == "intake_router"
        assert entry["status"] == "success"
        assert entry["duration_ms"] >= 0
        assert entry["input_hash"]
        assert entry["output_hash"]
