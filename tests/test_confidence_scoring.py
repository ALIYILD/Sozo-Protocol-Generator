"""Tests for confidence scoring module."""
from __future__ import annotations

import pytest

from sozo_generator.scoring.confidence import (
    ConfidenceBand,
    ConfidenceBreakdown,
    ConfidenceScorer,
    DataCompletenessInput,
    EvidenceStrengthInput,
    PhenotypeMatchInput,
)


@pytest.fixture
def scorer():
    return ConfidenceScorer()


# ── Input fixtures ────────────────────────────────────────────────────────


def _high_evidence():
    return EvidenceStrengthInput(
        overall_evidence_level="high",
        num_supporting_articles=15,
        num_rcts=5,
        num_meta_analyses=3,
        has_clinical_guideline=True,
        contradicting_evidence_count=0,
        evidence_recency_years=1.0,
    )


def _low_evidence():
    return EvidenceStrengthInput(
        overall_evidence_level="low",
        num_supporting_articles=2,
        num_rcts=0,
        num_meta_analyses=0,
        has_clinical_guideline=False,
        contradicting_evidence_count=3,
        evidence_recency_years=8.0,
    )


def _complete_data():
    return DataCompletenessInput(
        has_demographics=True,
        has_symptom_scores=True,
        num_symptom_scales=4,
        has_treatment_history=True,
        has_medications=True,
        has_eeg=True,
        has_brain_map=True,
        has_prior_response=True,
        total_assessments=4,
    )


def _missing_data():
    return DataCompletenessInput(
        has_demographics=False,
        has_symptom_scores=False,
        num_symptom_scales=0,
        has_treatment_history=False,
        has_medications=False,
        has_eeg=False,
        has_brain_map=False,
        has_prior_response=False,
        total_assessments=0,
    )


def _good_phenotype():
    return PhenotypeMatchInput(
        condition_slug="depression",
        matched_phenotype="melancholic",
        symptom_overlap_ratio=0.9,
        network_concordance=0.8,
        treatment_history_consistent=True,
    )


def _no_phenotype():
    return PhenotypeMatchInput(
        condition_slug="depression",
        matched_phenotype=None,
        symptom_overlap_ratio=0.0,
        network_concordance=0.0,
        treatment_history_consistent=False,
    )


# ── High confidence scenario ─────────────────────────────────────────────


class TestHighConfidence:
    def test_high_evidence_complete_data_good_phenotype(self, scorer):
        breakdown = scorer.score(_high_evidence(), _complete_data(), _good_phenotype())
        assert breakdown.band == ConfidenceBand.HIGH
        assert breakdown.composite_score >= 0.7

    def test_review_recommendation_for_high(self, scorer):
        breakdown = scorer.score(_high_evidence(), _complete_data(), _good_phenotype())
        assert "Standard" in breakdown.review_recommendation


# ── Low confidence scenario ──────────────────────────────────────────────


class TestLowConfidence:
    def test_low_evidence_missing_data_no_phenotype(self, scorer):
        breakdown = scorer.score(_low_evidence(), _missing_data(), _no_phenotype())
        assert breakdown.band == ConfidenceBand.LOW
        assert breakdown.composite_score < 0.4

    def test_review_recommendation_for_low(self, scorer):
        breakdown = scorer.score(_low_evidence(), _missing_data(), _no_phenotype())
        assert "Specialist" in breakdown.review_recommendation


# ── missing_data_impact ──────────────────────────────────────────────────


class TestMissingDataImpact:
    def test_identifies_missing_symptom_scores(self, scorer):
        breakdown = scorer.score(_high_evidence(), _missing_data(), _no_phenotype())
        impact_text = " ".join(breakdown.missing_data_impact)
        assert "symptom" in impact_text.lower()

    def test_identifies_missing_eeg(self, scorer):
        data = DataCompletenessInput(
            has_demographics=True,
            has_symptom_scores=True,
            num_symptom_scales=2,
            has_treatment_history=True,
            has_medications=True,
            has_eeg=False,
            has_brain_map=False,
            has_prior_response=True,
            total_assessments=2,
        )
        breakdown = scorer.score(_high_evidence(), data, _good_phenotype())
        impact_text = " ".join(breakdown.missing_data_impact)
        assert "EEG" in impact_text

    def test_no_missing_data_when_complete(self, scorer):
        breakdown = scorer.score(_high_evidence(), _complete_data(), _good_phenotype())
        # Only phenotype-related impact possible
        for item in breakdown.missing_data_impact:
            assert "symptom" not in item.lower() or "scale" in item.lower()


# ── Edge cases ────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_all_zeros_produces_insufficient(self, scorer):
        ev = EvidenceStrengthInput(
            overall_evidence_level="missing",
            num_supporting_articles=0,
            num_rcts=0,
            num_meta_analyses=0,
            has_clinical_guideline=False,
            contradicting_evidence_count=0,
            evidence_recency_years=0.0,
        )
        breakdown = scorer.score(ev, _missing_data(), _no_phenotype())
        assert breakdown.composite_score < 0.4
        assert breakdown.band in (ConfidenceBand.LOW, ConfidenceBand.INSUFFICIENT)

    def test_all_maxed_produces_high(self, scorer):
        ev = EvidenceStrengthInput(
            overall_evidence_level="highest",
            num_supporting_articles=50,
            num_rcts=10,
            num_meta_analyses=5,
            has_clinical_guideline=True,
            contradicting_evidence_count=0,
            evidence_recency_years=0.5,
        )
        pheno = PhenotypeMatchInput(
            condition_slug="test",
            matched_phenotype="test_pheno",
            symptom_overlap_ratio=1.0,
            network_concordance=1.0,
            treatment_history_consistent=True,
        )
        breakdown = scorer.score(ev, _complete_data(), pheno)
        assert breakdown.band == ConfidenceBand.HIGH
        assert breakdown.composite_score >= 0.9


# ── Confidence band thresholds ────────────────────────────────────────────


class TestConfidenceBandClassification:
    def test_high_threshold(self):
        assert ConfidenceScorer._classify_band(0.7) == ConfidenceBand.HIGH
        assert ConfidenceScorer._classify_band(0.9) == ConfidenceBand.HIGH
        assert ConfidenceScorer._classify_band(1.0) == ConfidenceBand.HIGH

    def test_moderate_threshold(self):
        assert ConfidenceScorer._classify_band(0.4) == ConfidenceBand.MODERATE
        assert ConfidenceScorer._classify_band(0.69) == ConfidenceBand.MODERATE

    def test_low_threshold(self):
        assert ConfidenceScorer._classify_band(0.01) == ConfidenceBand.LOW
        assert ConfidenceScorer._classify_band(0.39) == ConfidenceBand.LOW

    def test_insufficient_threshold(self):
        assert ConfidenceScorer._classify_band(0.0) == ConfidenceBand.INSUFFICIENT


# ── Custom weights ────────────────────────────────────────────────────────


class TestCustomWeights:
    def test_custom_weights_that_sum_to_one(self):
        scorer = ConfidenceScorer(w_evidence=0.5, w_data=0.3, w_phenotype=0.2)
        assert scorer.W_EVIDENCE == 0.5

    def test_custom_weights_that_do_not_sum_to_one_raises(self):
        with pytest.raises(ValueError, match="sum to 1.0"):
            ConfidenceScorer(w_evidence=0.5, w_data=0.5, w_phenotype=0.5)
