"""Tests for patient and assessment models."""
from __future__ import annotations

from datetime import date, datetime

import pytest

from sozo_generator.schemas.patient import (
    VALIDATED_SCALES,
    AssessmentScale,
    BiologicalSex,
    Demographics,
    DrugClass,
    Handedness,
    MedicationRecord,
    PatientProfile,
    SymptomAssessment,
    TreatmentRecord,
    get_scale,
    list_scales_for_condition,
)


# ── Demographics validation ───────────────────────────────────────────────


class TestDemographics:
    def test_valid_demographics(self):
        d = Demographics(age=35, sex=BiologicalSex.MALE)
        assert d.age == 35
        assert d.handedness == Handedness.RIGHT

    def test_age_lower_bound(self):
        d = Demographics(age=0, sex=BiologicalSex.FEMALE)
        assert d.age == 0

    def test_age_upper_bound(self):
        d = Demographics(age=120, sex=BiologicalSex.OTHER)
        assert d.age == 120

    def test_age_below_zero_rejected(self):
        with pytest.raises(Exception):
            Demographics(age=-1, sex=BiologicalSex.MALE)

    def test_age_above_120_rejected(self):
        with pytest.raises(Exception):
            Demographics(age=121, sex=BiologicalSex.MALE)

    def test_pediatric_age_passes(self):
        """Pediatric patients are allowed, just flagged internally."""
        d = Demographics(age=5, sex=BiologicalSex.FEMALE)
        assert d.age == 5


# ── PatientProfile creation and helpers ───────────────────────────────────


@pytest.fixture
def sample_patient():
    return PatientProfile(
        patient_id="P001",
        demographics=Demographics(age=45, sex=BiologicalSex.FEMALE),
        conditions=["depression"],
        medications=[
            MedicationRecord(
                name="sertraline",
                drug_class=DrugClass.SSRI,
                dose="100 mg/day",
                start_date=date(2024, 1, 1),
            ),
            MedicationRecord(
                name="lorazepam",
                drug_class=DrugClass.BENZODIAZEPINE,
                dose="1 mg/day",
                start_date=date(2024, 3, 1),
                end_date=date(2024, 6, 1),
            ),
        ],
        symptoms=[
            SymptomAssessment(
                scale_name="phq9",
                abbreviation="PHQ-9",
                total_score=18,
                severity_band="moderately_severe",
            ),
        ],
    )


class TestPatientProfile:
    def test_creation(self, sample_patient):
        assert sample_patient.patient_id == "P001"
        assert len(sample_patient.medications) == 2

    def test_active_medications_filters_correctly(self, sample_patient):
        active = sample_patient.active_medications
        assert len(active) == 1
        assert active[0].name == "sertraline"

    def test_all_interaction_flags(self):
        patient = PatientProfile(
            patient_id="P002",
            demographics=Demographics(age=50, sex=BiologicalSex.MALE),
            medications=[
                MedicationRecord(
                    name="lithium",
                    drug_class=DrugClass.OTHER,
                    dose="600 mg/day",
                    interaction_flags=["narrow_therapeutic_index", "renal_monitoring"],
                ),
                MedicationRecord(
                    name="sertraline",
                    drug_class=DrugClass.SSRI,
                    dose="50 mg/day",
                    interaction_flags=["serotonergic"],
                ),
            ],
        )
        flags = patient.all_interaction_flags
        assert "narrow_therapeutic_index" in flags
        assert "serotonergic" in flags
        assert len(flags) == 3

    def test_latest_assessment(self, sample_patient):
        result = sample_patient.latest_assessment("PHQ-9")
        assert result is not None
        assert result.total_score == 18

    def test_latest_assessment_not_found(self, sample_patient):
        result = sample_patient.latest_assessment("GAD-7")
        assert result is None

    def test_has_contraindication(self):
        patient = PatientProfile(
            patient_id="P003",
            demographics=Demographics(age=55, sex=BiologicalSex.MALE),
            contraindications_patient=["cardiac pacemaker", "cochlear implant"],
        )
        assert patient.has_contraindication("pacemaker") is True
        assert patient.has_contraindication("skull plate") is False


# ── VALIDATED_SCALES registry ─────────────────────────────────────────────


class TestValidatedScalesRegistry:
    def test_get_scale_phq9(self):
        scale = get_scale("PHQ-9")
        assert scale is not None
        assert scale.abbreviation == "PHQ-9"
        assert scale.score_range.max == 27

    def test_get_scale_returns_none_for_unknown(self):
        assert get_scale("UNKNOWN-SCALE") is None

    def test_list_scales_for_depression(self):
        scales = list_scales_for_condition("depression")
        abbrs = [s.abbreviation for s in scales]
        assert "PHQ-9" in abbrs
        assert "BDI-II" in abbrs
        assert "MADRS" in abbrs

    def test_list_scales_for_parkinsons(self):
        scales = list_scales_for_condition("parkinsons")
        abbrs = [s.abbreviation for s in scales]
        assert "UPDRS-III" in abbrs

    def test_list_scales_for_nonexistent_condition(self):
        scales = list_scales_for_condition("nonexistent_condition_xyz")
        assert scales == []

    def test_registry_has_expected_keys(self):
        assert "PHQ-9" in VALIDATED_SCALES
        assert "GAD-7" in VALIDATED_SCALES
        assert "MoCA" in VALIDATED_SCALES
        assert "UPDRS-III" in VALIDATED_SCALES


# ── AssessmentScale.classify_severity() for PHQ-9 ─────────────────────────


class TestClassifySeverityPHQ9:
    @pytest.fixture
    def phq9(self):
        return VALIDATED_SCALES["PHQ-9"]

    def test_minimal_severity(self, phq9):
        assert phq9.classify_severity(0) == "minimal"
        assert phq9.classify_severity(4) == "minimal"

    def test_mild_severity(self, phq9):
        assert phq9.classify_severity(5) == "mild"
        assert phq9.classify_severity(9) == "mild"

    def test_moderate_severity(self, phq9):
        assert phq9.classify_severity(10) == "moderate"
        assert phq9.classify_severity(14) == "moderate"

    def test_moderately_severe(self, phq9):
        assert phq9.classify_severity(15) == "moderately_severe"
        assert phq9.classify_severity(19) == "moderately_severe"

    def test_severe(self, phq9):
        assert phq9.classify_severity(20) == "severe"
        assert phq9.classify_severity(27) == "severe"

    def test_out_of_range_returns_none(self, phq9):
        assert phq9.classify_severity(28) is None
        assert phq9.classify_severity(-1) is None

    def test_is_valid_score(self, phq9):
        assert phq9.is_valid_score(0) is True
        assert phq9.is_valid_score(27) is True
        assert phq9.is_valid_score(28) is False
        assert phq9.is_valid_score(-1) is False


# ── MedicationRecord.is_active property ───────────────────────────────────


class TestMedicationRecordIsActive:
    def test_active_when_no_end_date(self):
        med = MedicationRecord(
            name="sertraline", drug_class=DrugClass.SSRI, dose="50 mg/day",
        )
        assert med.is_active is True

    def test_inactive_when_end_date_set(self):
        med = MedicationRecord(
            name="sertraline",
            drug_class=DrugClass.SSRI,
            dose="50 mg/day",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 6, 1),
        )
        assert med.is_active is False


# ── TreatmentRecord date validation ──────────────────────────────────────


class TestTreatmentRecordDates:
    def test_valid_date_range(self):
        tr = TreatmentRecord(
            modality="tdcs",
            condition_slug="depression",
            target="L-DLPFC",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 3, 1),
        )
        assert tr.start_date < tr.end_date

    def test_same_start_and_end(self):
        tr = TreatmentRecord(
            modality="tdcs",
            condition_slug="depression",
            target="L-DLPFC",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 1),
        )
        assert tr.start_date == tr.end_date

    def test_end_before_start_rejected(self):
        with pytest.raises(Exception, match="end_date"):
            TreatmentRecord(
                modality="tdcs",
                condition_slug="depression",
                target="L-DLPFC",
                start_date=date(2024, 6, 1),
                end_date=date(2024, 1, 1),
            )

    def test_no_dates_is_valid(self):
        tr = TreatmentRecord(
            modality="tdcs",
            condition_slug="depression",
            target="L-DLPFC",
        )
        assert tr.start_date is None
        assert tr.end_date is None
