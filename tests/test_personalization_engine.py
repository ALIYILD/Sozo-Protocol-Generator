"""Tests for the personalization engine and its sub-components."""
from __future__ import annotations

import pytest

from sozo_personalization.engine import PersonalizationEngine, UNIVERSAL_CONTRAINDICATIONS
from sozo_personalization.models import PersonalizationRequest, PersonalizationResult
from sozo_personalization.phenotype_matcher import PhenotypeMatcher
from sozo_personalization.protocol_ranker import ProtocolRanker
from sozo_personalization.eeg_analyzer import EEGAnalyzer


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def depression_schema():
    """Minimal condition schema dict for depression."""
    return {
        "slug": "depression",
        "display_name": "Major Depressive Disorder",
        "icd10": "F32.1",
        "overall_evidence_quality": "high",
        "phenotypes": [
            {
                "slug": "melancholic",
                "label": "Melancholic Depression",
                "key_features": [
                    "anhedonia", "psychomotor retardation", "early morning awakening",
                    "diurnal variation", "weight loss",
                ],
                "preferred_modalities": ["tdcs"],
            },
            {
                "slug": "anxious",
                "label": "Anxious Depression",
                "key_features": [
                    "anxiety", "worry", "restlessness", "insomnia", "irritability",
                ],
                "preferred_modalities": ["tavns"],
            },
        ],
        "protocols": [
            {
                "protocol_id": "dep-tdcs-001",
                "modality": "tdcs",
                "target_region": "Left DLPFC",
                "target_abbreviation": "L-DLPFC",
                "parameters": {"current_mA": 2.0, "duration_min": 20},
                "evidence_level": "high",
                "phenotype_slugs": ["melancholic"],
                "rationale": "Standard L-DLPFC tDCS for depression",
                "session_count": 20,
            },
            {
                "protocol_id": "dep-tavns-001",
                "modality": "tavns",
                "target_region": "Left Tragus",
                "target_abbreviation": "L-Tragus",
                "parameters": {"frequency_hz": 25, "pulse_width_us": 250},
                "evidence_level": "medium",
                "phenotype_slugs": ["anxious"],
                "rationale": "taVNS for anxious depression",
                "session_count": 15,
            },
        ],
        "contraindications": [],
        "exclusion_criteria": [],
        "references": [
            {"type": "rct", "pmid": "12345678"},
            {"type": "meta_analysis", "pmid": "23456789"},
        ],
    }


@pytest.fixture
def minimal_request():
    return PersonalizationRequest(
        condition_slug="depression",
        patient_demographics={"age": 40, "sex": "female"},
        symptoms=[
            {"name": "anhedonia"},
            {"name": "psychomotor retardation"},
            {"name": "weight loss"},
        ],
        medications=[],
        treatment_history=[],
        medical_history=[],
    )


# ── PhenotypeMatcher ─────────────────────────────────────────────────────


class TestPhenotypeMatcher:
    def test_matches_depression_with_phq9_symptoms(self, depression_schema):
        matcher = PhenotypeMatcher()
        result = matcher.match(
            phenotypes=depression_schema["phenotypes"],
            patient_symptoms=[
                {"name": "anhedonia"},
                {"name": "psychomotor retardation"},
                {"name": "diurnal variation"},
            ],
        )
        assert result.phenotype_slug == "melancholic"
        assert result.confidence > 0.0
        assert len(result.matched_features) >= 2

    def test_no_phenotypes_returns_empty_match(self):
        matcher = PhenotypeMatcher()
        result = matcher.match(
            phenotypes=[],
            patient_symptoms=[{"name": "anhedonia"}],
        )
        assert result.phenotype_slug is None
        assert result.confidence == 0.0

    def test_no_symptoms_returns_low_confidence(self, depression_schema):
        matcher = PhenotypeMatcher()
        result = matcher.match(
            phenotypes=depression_schema["phenotypes"],
            patient_symptoms=[],
        )
        assert result.confidence < 0.2


# ── ProtocolRanker ────────────────────────────────────────────────────────


class TestProtocolRanker:
    def test_scores_and_sorts_candidates(self, depression_schema):
        ranker = ProtocolRanker()
        ranked = ranker.rank(
            protocols=depression_schema["protocols"],
            matched_phenotype_slug="melancholic",
            phenotype_confidence=0.8,
            treatment_history=[],
            blocked_modalities=[],
            restricted_modalities=[],
        )
        assert len(ranked) == 2
        # Sorted descending by score
        assert ranked[0].score >= ranked[1].score

    def test_blocked_modality_excluded(self, depression_schema):
        ranker = ProtocolRanker()
        ranked = ranker.rank(
            protocols=depression_schema["protocols"],
            matched_phenotype_slug="melancholic",
            phenotype_confidence=0.8,
            treatment_history=[],
            blocked_modalities=["tdcs"],
            restricted_modalities=[],
        )
        modalities = [c.modality for c in ranked]
        assert "tdcs" not in modalities

    def test_empty_protocols_returns_empty(self):
        ranker = ProtocolRanker()
        ranked = ranker.rank(
            protocols=[],
            matched_phenotype_slug=None,
            phenotype_confidence=0.0,
            treatment_history=[],
            blocked_modalities=[],
            restricted_modalities=[],
        )
        assert ranked == []


# ── EEGAnalyzer ──────────────────────────────────────────────────────────


class TestEEGAnalyzer:
    def test_basic_band_power_analysis(self):
        analyzer = EEGAnalyzer()
        result = analyzer.analyze(
            eeg_features={
                "peak_alpha_frequency": 8.5,
                "frontal_alpha_asymmetry": -0.2,
                "theta_beta_ratio": 3.0,
                "network_dysfunction_map": {"dmn": "moderate"},
                "confidence": 0.8,
                "abnormal_regions": [],
                "suggested_targets": [],
            },
            condition_slug="depression",
        )
        assert result.quality_adequate is True
        assert len(result.adjustments) >= 1
        assert result.explanation != ""

    def test_low_quality_skips_adjustments(self):
        analyzer = EEGAnalyzer()
        result = analyzer.analyze(
            eeg_features={
                "peak_alpha_frequency": 10.0,
                "frontal_alpha_asymmetry": 0.0,
                "theta_beta_ratio": 3.0,
                "confidence": 0.2,
            },
            condition_slug="depression",
        )
        assert result.quality_adequate is False
        assert result.adjustments == []


# ── PersonalizationEngine end-to-end ──────────────────────────────────────


class TestPersonalizationEngine:
    def test_end_to_end_minimal_input(self, depression_schema, minimal_request):
        engine = PersonalizationEngine(depression_schema)
        result = engine.personalize(minimal_request)

        assert isinstance(result, PersonalizationResult)
        assert result.condition_slug == "depression"
        assert result.safety_cleared is True
        assert result.recommended_protocol is not None
        assert result.confidence_score > 0

    def test_safety_layer_blocks_contraindicated_modalities(self, depression_schema):
        request = PersonalizationRequest(
            condition_slug="depression",
            patient_demographics={"age": 40, "sex": "male"},
            symptoms=[{"name": "anhedonia"}],
            medications=[],
            treatment_history=[],
            medical_history=["cardiac pacemaker"],
        )
        engine = PersonalizationEngine(depression_schema)
        result = engine.personalize(request)

        assert result.safety_cleared is False
        assert len(result.blocked_modalities) > 0
        assert "tdcs" in result.blocked_modalities

    def test_decision_trace_is_populated(self, depression_schema, minimal_request):
        engine = PersonalizationEngine(depression_schema)
        result = engine.personalize(minimal_request)

        assert len(result.decision_trace) == 4
        layer_names = [t["name"] for t in result.decision_trace]
        assert "safety" in layer_names
        assert "selection" in layer_names
        assert "eeg_refinement" in layer_names
        assert "explanation" in layer_names

    def test_eeg_features_trigger_refinement(self, depression_schema):
        request = PersonalizationRequest(
            condition_slug="depression",
            patient_demographics={"age": 40, "sex": "female"},
            symptoms=[{"name": "anhedonia"}],
            medications=[],
            treatment_history=[],
            medical_history=[],
            eeg_features={
                "peak_alpha_frequency": 8.0,
                "frontal_alpha_asymmetry": -0.3,
                "theta_beta_ratio": 3.5,
                "network_dysfunction_map": {"cen": "moderate"},
                "confidence": 0.85,
                "abnormal_regions": ["left DLPFC"],
                "suggested_targets": ["L-DLPFC"],
            },
        )
        engine = PersonalizationEngine(depression_schema)
        result = engine.personalize(request)

        assert len(result.eeg_adjustments) >= 1
        assert result.target_refinement is not None
