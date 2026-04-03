"""Tests for SozoProtocol Pydantic model and sub-models."""
from __future__ import annotations

import json
from datetime import datetime
from uuid import uuid4

import pytest

from sozo_generator.core.enums import EvidenceLevel, EvidenceType, Modality
from sozo_generator.schemas.protocol import (
    AuditMetadata,
    ConditionInfo,
    EvidenceReference,
    GenerationMethod,
    IntensityParams,
    ModalityInfo,
    Montage,
    ProtocolStatus,
    Safety,
    Schedule,
    SozoProtocol,
    StimulationParameters,
    StimulationTarget,
    get_protocol_json_schema,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def minimal_evidence_ref():
    """A single valid evidence reference."""
    return EvidenceReference(
        pmid="12345678",
        year=2023,
        evidence_type=EvidenceType.RCT,
        evidence_level=EvidenceLevel.HIGH,
        relevance_score=4.0,
    )


@pytest.fixture
def minimal_condition():
    return ConditionInfo(
        slug="depression",
        display_name="Major Depressive Disorder",
        icd10="F32.1",
    )


@pytest.fixture
def minimal_stim_params():
    return StimulationParameters(
        target=StimulationTarget(primary_site="L-DLPFC"),
        montage=Montage(),
        intensity=IntensityParams(value=2.0, unit="mA"),
        duration_minutes=20,
    )


@pytest.fixture
def minimal_protocol(minimal_condition, minimal_stim_params, minimal_evidence_ref):
    """A SozoProtocol with only required fields."""
    return SozoProtocol(
        condition=minimal_condition,
        modality=ModalityInfo(primary=Modality.TDCS),
        stimulation_parameters=minimal_stim_params,
        schedule=Schedule(total_sessions=10, frequency="5x/week"),
        safety=Safety(),
        evidence_references=[minimal_evidence_ref],
        audit=AuditMetadata(created_by="test"),
    )


# ── SozoProtocol instantiation ────────────────────────────────────────────


class TestSozoProtocolInstantiation:
    def test_minimal_required_fields(self, minimal_protocol):
        """Protocol can be created with only required fields."""
        assert minimal_protocol.version == 1
        assert minimal_protocol.status == ProtocolStatus.DRAFT
        assert minimal_protocol.condition.slug == "depression"
        assert minimal_protocol.personalization is None

    def test_all_fields(self, minimal_condition, minimal_stim_params, minimal_evidence_ref):
        """Protocol can be created with all optional fields populated."""
        proto = SozoProtocol(
            protocol_id=uuid4(),
            version=2,
            parent_version_id=uuid4(),
            status=ProtocolStatus.APPROVED,
            condition=minimal_condition,
            modality=ModalityInfo(
                primary=Modality.TDCS,
                secondary=[Modality.TAVNS],
                rationale="Combined protocol",
            ),
            stimulation_parameters=minimal_stim_params,
            schedule=Schedule(total_sessions=20, frequency="3x/week"),
            safety=Safety(precautions=["Monitor BP"]),
            evidence_references=[minimal_evidence_ref],
            expected_outcomes=[],
            audit=AuditMetadata(
                created_by="test",
                generation_method=GenerationMethod.PERSONALIZED,
                build_id="build-001",
            ),
        )
        assert proto.version == 2
        assert proto.status == ProtocolStatus.APPROVED
        assert proto.modality.secondary == [Modality.TAVNS]


# ── JSON Schema generation ────────────────────────────────────────────────


class TestJsonSchemaGeneration:
    def test_json_schema_returns_dict(self):
        schema = get_protocol_json_schema()
        assert isinstance(schema, dict)
        assert "title" in schema
        assert schema["title"] == "SozoProtocol"

    def test_json_schema_has_properties(self):
        schema = get_protocol_json_schema()
        assert "properties" in schema
        assert "condition" in schema["properties"]
        assert "evidence_references" in schema["properties"]


# ── Serialization round-trip ──────────────────────────────────────────────


class TestSerializationRoundTrip:
    def test_json_round_trip(self, minimal_protocol):
        json_str = minimal_protocol.model_dump_json()
        data = json.loads(json_str)
        restored = SozoProtocol(**data)
        assert str(restored.protocol_id) == str(minimal_protocol.protocol_id)
        assert restored.condition.slug == minimal_protocol.condition.slug
        assert len(restored.evidence_references) == 1

    def test_dict_round_trip(self, minimal_protocol):
        data = minimal_protocol.model_dump()
        restored = SozoProtocol(**data)
        assert restored.version == minimal_protocol.version


# ── Field validation ──────────────────────────────────────────────────────


class TestFieldValidation:
    def test_invalid_icd10_format(self):
        with pytest.raises(Exception):
            ConditionInfo(
                slug="test",
                display_name="Test",
                icd10="INVALID",
            )

    def test_valid_icd10_codes(self):
        c1 = ConditionInfo(slug="test", display_name="Test", icd10="F32.1")
        assert c1.icd10 == "F32.1"
        c2 = ConditionInfo(slug="test", display_name="Test", icd10="G20")
        assert c2.icd10 == "G20"

    def test_negative_intensity_rejected(self):
        with pytest.raises(Exception):
            IntensityParams(value=-1.0, unit="mA")

    def test_zero_intensity_rejected(self):
        with pytest.raises(Exception):
            IntensityParams(value=0, unit="mA")

    def test_invalid_pmid_format(self):
        with pytest.raises(Exception):
            EvidenceReference(
                pmid="not-a-number",
                year=2023,
                evidence_type=EvidenceType.RCT,
                evidence_level=EvidenceLevel.HIGH,
                relevance_score=3.0,
            )

    def test_pmid_too_long(self):
        with pytest.raises(Exception):
            EvidenceReference(
                pmid="1234567890",  # 10 digits, max is 9
                year=2023,
                evidence_type=EvidenceType.RCT,
                evidence_level=EvidenceLevel.HIGH,
                relevance_score=3.0,
            )


# ── ProtocolStatus enum ───────────────────────────────────────────────────


class TestProtocolStatusEnum:
    def test_draft_value(self):
        assert ProtocolStatus.DRAFT.value == "draft"

    def test_all_statuses_are_strings(self):
        for s in ProtocolStatus:
            assert isinstance(s.value, str)


# ── ConditionInfo slug validation ─────────────────────────────────────────


class TestConditionInfoSlug:
    def test_valid_slug(self):
        c = ConditionInfo(slug="depression", display_name="D", icd10="F32")
        assert c.slug == "depression"

    def test_slug_with_underscore(self):
        c = ConditionInfo(slug="chronic_pain", display_name="CP", icd10="G89")
        assert c.slug == "chronic_pain"

    def test_slug_with_numbers(self):
        c = ConditionInfo(slug="adhd2", display_name="ADHD2", icd10="F90")
        assert c.slug == "adhd2"

    def test_invalid_slug_uppercase(self):
        with pytest.raises(Exception):
            ConditionInfo(slug="Depression", display_name="D", icd10="F32")

    def test_invalid_slug_starts_with_number(self):
        with pytest.raises(Exception):
            ConditionInfo(slug="2fast", display_name="D", icd10="F32")

    def test_invalid_slug_with_hyphen(self):
        with pytest.raises(Exception):
            ConditionInfo(slug="chronic-pain", display_name="D", icd10="G89")


# ── StimulationParameters bounds ──────────────────────────────────────────


class TestStimulationParametersBounds:
    def test_duration_lower_bound(self):
        sp = StimulationParameters(
            target=StimulationTarget(primary_site="L-DLPFC"),
            montage=Montage(),
            intensity=IntensityParams(value=2.0, unit="mA"),
            duration_minutes=1,
        )
        assert sp.duration_minutes == 1

    def test_duration_upper_bound(self):
        sp = StimulationParameters(
            target=StimulationTarget(primary_site="L-DLPFC"),
            montage=Montage(),
            intensity=IntensityParams(value=2.0, unit="mA"),
            duration_minutes=120,
        )
        assert sp.duration_minutes == 120

    def test_duration_below_lower_bound(self):
        with pytest.raises(Exception):
            StimulationParameters(
                target=StimulationTarget(primary_site="L-DLPFC"),
                montage=Montage(),
                intensity=IntensityParams(value=2.0, unit="mA"),
                duration_minutes=0.5,
            )

    def test_duration_above_upper_bound(self):
        with pytest.raises(Exception):
            StimulationParameters(
                target=StimulationTarget(primary_site="L-DLPFC"),
                montage=Montage(),
                intensity=IntensityParams(value=2.0, unit="mA"),
                duration_minutes=121,
            )


# ── evidence_references min_length ────────────────────────────────────────


class TestEvidenceReferencesConstraint:
    def test_empty_evidence_references_rejected(
        self, minimal_condition, minimal_stim_params,
    ):
        with pytest.raises(Exception):
            SozoProtocol(
                condition=minimal_condition,
                modality=ModalityInfo(primary=Modality.TDCS),
                stimulation_parameters=minimal_stim_params,
                schedule=Schedule(total_sessions=10, frequency="5x/week"),
                safety=Safety(),
                evidence_references=[],
                audit=AuditMetadata(created_by="test"),
            )
