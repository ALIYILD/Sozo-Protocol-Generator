"""Tests for patient/session/outcome models and persistence."""
import pytest
from pathlib import Path


class TestPatientModels:
    def test_patient_creation(self):
        from sozo_session.models import Patient
        p = Patient(name="John Doe", condition_slugs=["parkinsons"])
        assert p.patient_id.startswith("pat-")
        assert p.name == "John Doe"
        assert "parkinsons" in p.condition_slugs

    def test_session_record(self):
        from sozo_session.models import SessionRecord
        s = SessionRecord(patient_id="pat-001", condition_slug="depression", status="completed")
        assert s.session_id.startswith("sess-")
        assert s.status == "completed"

    def test_outcome_record(self):
        from sozo_session.models import OutcomeRecord
        o = OutcomeRecord(patient_id="pat-001", assessment_tool="PHQ-9", score=12, score_max=27, timepoint="week4")
        assert o.assessment_tool == "PHQ-9"
        assert o.timepoint == "week4"

    def test_treatment_plan(self):
        from sozo_session.models import TreatmentPlan
        t = TreatmentPlan(patient_id="pat-001", condition_slug="parkinsons", total_sessions=12)
        assert t.plan_id.startswith("plan-")
        assert t.total_sessions == 12

    def test_session_from_result(self):
        """SessionRecord can be created from SessionResult."""
        from sozo_session.models import SessionRecord
        # Simulate a SessionResult-like object
        class FakeResult:
            session_id = "sess-fake"
            patient_id = "pat-001"
            status = "completed"
            started_at = "2026-04-03T10:00:00Z"
            completed_at = "2026-04-03T11:30:00Z"
            duration_min = 90.0
            steps_completed = 7
            steps_total = 7
            adverse_events = []
            impedance_pre = {"ch1": 3.5}
            impedance_post = {"ch1": 3.2}

        sr = SessionRecord.from_session_result(FakeResult())
        assert sr.session_id == "sess-fake"
        assert sr.steps_completed == 7


class TestPatientStore:
    def test_save_and_load(self, tmp_path):
        from sozo_session.store import PatientStore
        from sozo_session.models import Patient

        store = PatientStore(tmp_path / "patients")
        p = Patient(name="Test Patient", condition_slugs=["adhd"])
        store.save(p)
        loaded = store.load(p.patient_id)
        assert loaded is not None
        assert loaded.name == "Test Patient"

    def test_list_patients(self, tmp_path):
        from sozo_session.store import PatientStore
        from sozo_session.models import Patient

        store = PatientStore(tmp_path / "patients")
        for i in range(3):
            store.save(Patient(name=f"Patient {i}"))
        patients = store.list()
        assert len(patients) == 3

    def test_search_by_condition(self, tmp_path):
        from sozo_session.store import PatientStore
        from sozo_session.models import Patient

        store = PatientStore(tmp_path / "patients")
        store.save(Patient(name="PD Patient", condition_slugs=["parkinsons"]))
        store.save(Patient(name="Dep Patient", condition_slugs=["depression"]))

        pd_patients = store.search_by_condition("parkinsons")
        assert len(pd_patients) == 1
        assert pd_patients[0].name == "PD Patient"


class TestSessionStore:
    def test_save_and_load(self, tmp_path):
        from sozo_session.store import SessionStore
        from sozo_session.models import SessionRecord

        store = SessionStore(tmp_path / "sessions")
        s = SessionRecord(patient_id="pat-001", condition_slug="parkinsons", status="completed")
        store.save(s)
        loaded = store.load(s.session_id)
        assert loaded is not None
        assert loaded.status == "completed"

    def test_list_for_patient(self, tmp_path):
        from sozo_session.store import SessionStore
        from sozo_session.models import SessionRecord

        store = SessionStore(tmp_path / "sessions")
        store.save(SessionRecord(patient_id="pat-001", status="completed"))
        store.save(SessionRecord(patient_id="pat-001", status="completed"))
        store.save(SessionRecord(patient_id="pat-002", status="completed"))

        p1_sessions = store.list_for_patient("pat-001")
        assert len(p1_sessions) == 2


class TestOutcomeStore:
    def test_save_and_load(self, tmp_path):
        from sozo_session.store import OutcomeStore
        from sozo_session.models import OutcomeRecord

        store = OutcomeStore(tmp_path / "outcomes")
        o = OutcomeRecord(patient_id="pat-001", assessment_tool="UPDRS", score=28)
        store.save(o)
        loaded = store.load(o.outcome_id)
        assert loaded is not None
        assert loaded.score == 28

    def test_list_for_patient(self, tmp_path):
        from sozo_session.store import OutcomeStore
        from sozo_session.models import OutcomeRecord

        store = OutcomeStore(tmp_path / "outcomes")
        store.save(OutcomeRecord(patient_id="pat-001", assessment_tool="PHQ-9", score=12))
        store.save(OutcomeRecord(patient_id="pat-001", assessment_tool="MoCA", score=26))

        outcomes = store.list_for_patient("pat-001")
        assert len(outcomes) == 2
