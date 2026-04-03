"""Tests for the safety module: drug interactions, interaction checker, and contraindication engine."""
from __future__ import annotations

import pytest

from sozo_generator.safety.drug_interactions import (
    DRUG_INTERACTIONS,
    get_interactions_for_drug_class,
    get_interactions_for_modality,
)
from sozo_generator.safety.interaction_checker import (
    InteractionCheckResult,
    check_interactions,
)
from sozo_generator.safety.contraindication_engine import (
    PatientSafetyProfile,
    evaluate_patient_safety,
)


# ── DRUG_INTERACTIONS database ────────────────────────────────────────────


class TestDrugInteractionsDatabase:
    def test_database_is_non_empty(self):
        assert len(DRUG_INTERACTIONS) > 0

    def test_has_lithium_entry(self):
        lithium = [d for d in DRUG_INTERACTIONS if d.drug_class == "lithium"]
        assert len(lithium) >= 1

    def test_has_ssri_entry(self):
        ssris = [d for d in DRUG_INTERACTIONS if d.drug_class == "ssris"]
        assert len(ssris) >= 1

    def test_has_benzodiazepine_entry(self):
        benzos = [d for d in DRUG_INTERACTIONS if d.drug_class == "benzodiazepines"]
        assert len(benzos) >= 1

    def test_has_anticoagulant_entry(self):
        anti = [d for d in DRUG_INTERACTIONS if d.drug_class == "anticoagulants"]
        assert len(anti) >= 1

    def test_all_entries_have_required_fields(self):
        for interaction in DRUG_INTERACTIONS:
            assert interaction.drug_class
            assert isinstance(interaction.modalities_affected, list)
            assert interaction.severity in (
                "contraindicated", "major", "moderate", "minor",
            )
            assert interaction.mechanism
            assert interaction.recommendation


# ── get_interactions_for_drug_class ───────────────────────────────────────


class TestGetInteractionsForDrugClass:
    def test_lithium_returns_results(self):
        results = get_interactions_for_drug_class("lithium")
        assert len(results) >= 1
        assert results[0].drug_class == "lithium"

    def test_case_insensitive(self):
        results = get_interactions_for_drug_class("LITHIUM")
        assert len(results) >= 1

    def test_match_by_generic_example(self):
        results = get_interactions_for_drug_class("sertraline")
        assert len(results) >= 1

    def test_unknown_drug_returns_empty(self):
        results = get_interactions_for_drug_class("nonexistent_drug_xyz")
        assert results == []


# ── get_interactions_for_modality ─────────────────────────────────────────


class TestGetInteractionsForModality:
    def test_tdcs_returns_results(self):
        results = get_interactions_for_modality("tdcs")
        assert len(results) >= 5

    def test_tps_returns_results(self):
        results = get_interactions_for_modality("tps")
        assert len(results) >= 1

    def test_tavns_returns_results(self):
        results = get_interactions_for_modality("tavns")
        assert len(results) >= 1

    def test_unknown_modality_returns_empty(self):
        results = get_interactions_for_modality("nonexistent_modality")
        assert results == []


# ── check_interactions ────────────────────────────────────────────────────


class TestCheckInteractions:
    def test_lithium_produces_major_interaction(self):
        meds = [{"name": "lithium_carbonate", "drug_class": "lithium"}]
        result = check_interactions(meds)
        assert result.has_major_interactions is True
        assert len(result.interactions) >= 1
        severities = {a.severity for a in result.interactions}
        assert "major" in severities

    def test_no_medications_all_safe(self):
        result = check_interactions([])
        assert result.is_safe is True
        assert result.has_contraindications is False
        assert result.has_major_interactions is False
        assert "No medication interactions detected" in result.summary

    def test_safe_modalities_computed(self):
        result = check_interactions([])
        assert sorted(result.safe_modalities) == ["ces", "tavns", "tdcs", "tps"]

    def test_restricted_modalities_with_lithium(self):
        meds = [{"name": "lithium", "drug_class": "lithium"}]
        result = check_interactions(meds)
        # Lithium is major for all four modalities
        assert len(result.restricted_modalities) >= 1 or len(result.blocked_modalities) >= 1

    def test_target_modalities_filter(self):
        meds = [{"name": "lithium", "drug_class": "lithium"}]
        result = check_interactions(meds, target_modalities=["tdcs"])
        # Should only flag interactions for tdcs
        for alert in result.interactions:
            assert alert.modality == "tdcs"


# ── evaluate_patient_safety ──────────────────────────────────────────────


class TestEvaluatePatientSafety:
    def test_clean_adult_patient_cleared(self):
        result = evaluate_patient_safety(
            patient_demographics={"age": 35, "sex": "male", "patient_id": "P001"},
            medications=[],
            medical_history=[],
        )
        assert result.safety_cleared is True
        assert result.absolute_contraindications == []
        assert result.patient_id == "P001"

    def test_pediatric_patient_blocked(self):
        result = evaluate_patient_safety(
            patient_demographics={"age": 12, "sex": "female", "patient_id": "P002"},
            medications=[],
            medical_history=[],
        )
        assert result.safety_cleared is False
        # All modalities should be blocked for pediatric
        for modality, cleared in result.modality_clearance.items():
            assert cleared is False

    def test_elderly_patient_has_warnings(self):
        result = evaluate_patient_safety(
            patient_demographics={"age": 85, "sex": "male", "patient_id": "P003"},
            medications=[],
            medical_history=[],
        )
        assert result.safety_cleared is True
        assert len(result.age_considerations) >= 1
        # Should mention age >80
        age_text = " ".join(result.age_considerations)
        assert "80" in age_text or "elderly" in age_text.lower()

    def test_medication_interactions_populated(self):
        result = evaluate_patient_safety(
            patient_demographics={"age": 40, "sex": "male"},
            medications=[{"name": "lithium_carbonate", "drug_class": "lithium"}],
            medical_history=[],
        )
        assert result.medication_interactions.has_major_interactions is True

    def test_summary_cleared(self):
        result = evaluate_patient_safety(
            patient_demographics={"age": 40, "sex": "female"},
            medications=[],
            medical_history=[],
        )
        assert "cleared" in result.summary.lower()

    def test_summary_not_cleared_for_pediatric(self):
        result = evaluate_patient_safety(
            patient_demographics={"age": 10, "sex": "male"},
            medications=[],
            medical_history=[],
        )
        assert "NOT cleared" in result.summary
