"""Tests for structure-native DocumentSpec invariants (Phase 3 deep)."""
from __future__ import annotations

from autoagent_clinical.evaluators import evaluate_document_spec_invariants
from autoagent_clinical.runner import evaluate_case_result
from autoagent_clinical.schemas import (
    BenchmarkCase,
    BenchmarkExpectations,
    HarnessMetadata,
    HarnessResult,
)
from autoagent_clinical.validators import run_document_spec_invariants_validation


def _minimal_ebp_spec(**overrides):
    from sozo_generator.core.enums import DocumentType, Tier
    from sozo_generator.schemas.documents import DocumentSpec, SectionContent

    # Top-level order matches relaxed canonical template (see validator).
    sections = [
        SectionContent(
            section_id="document_control",
            title="Control",
            content="Doc control.",
        ),
        SectionContent(
            section_id="inclusion_exclusion",
            title="Inclusion",
            content="Ix/Ex.",
        ),
        SectionContent(
            section_id="clinical_overview",
            title="Overview",
            content="Clinical overview text.",
        ),
        SectionContent(
            section_id="pathophysiology",
            title="Pathophysiology",
            content="Mechanisms.",
        ),
        SectionContent(
            section_id="brain_anatomy",
            title="Anatomy",
            content="Regions.",
        ),
        SectionContent(
            section_id="phenotypes",
            title="Phenotypes",
            content="Types.",
        ),
        SectionContent(
            section_id="protocols_tdcs",
            title="tDCS",
            content="Montage.",
        ),
        SectionContent(
            section_id="protocols_tps",
            title="TPS",
            content="Pulse.",
        ),
        SectionContent(
            section_id="safety",
            title="Safety",
            content="Rules and monitoring.",
        ),
        SectionContent(
            section_id="assessments",
            title="Assessments",
            content="Scales.",
        ),
        SectionContent(
            section_id="responder_criteria",
            title="Responder",
            content="Criteria.",
        ),
        SectionContent(
            section_id="followup",
            title="Follow-up",
            content="Plan.",
        ),
        SectionContent(
            section_id="evidence_summary",
            title="Evidence",
            content="Summary.",
        ),
        SectionContent(
            section_id="references",
            title="References",
            content="PMID: 12345678",
        ),
    ]
    base = dict(
        document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
        tier=Tier.FELLOW,
        condition_slug="parkinsons",
        condition_name="Parkinson's Disease",
        title="SOZO Evidence-Based Protocol — Parkinson's Disease",
        sections=sections,
        references=[{"title": f"Ref {i}", "pmid": str(10000000 + i)} for i in range(5)],
    )
    base.update(overrides)
    return DocumentSpec(**base).model_dump(mode="json")


def test_invariants_valid_relaxed() -> None:
    payload = _minimal_ebp_spec()
    rep = run_document_spec_invariants_validation(
        payload,
        case_inputs={"document_invariant_mode": "relaxed", "min_document_references": 3},
    )
    assert rep.validator_id == "document_spec_invariants"
    assert not any(f.code == "missing_required_section" for f in rep.findings)


def test_invariants_missing_critical_section() -> None:
    from sozo_generator.core.enums import DocumentType, Tier
    from sozo_generator.schemas.documents import DocumentSpec, SectionContent

    spec = DocumentSpec(
        document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
        tier=Tier.FELLOW,
        condition_slug="parkinsons",
        condition_name="Parkinson's Disease",
        title="SOZO Evidence-Based Protocol — Parkinson's Disease",
        sections=[
            SectionContent(section_id="clinical_overview", title="X", content="Y"),
            SectionContent(section_id="protocols_tdcs", title="P", content="c"),
        ],
        references=[{"x": 1}, {"x": 2}, {"x": 3}],
    )
    rep = run_document_spec_invariants_validation(
        spec.model_dump(mode="json"),
        case_inputs={"document_invariant_mode": "relaxed"},
    )
    codes = [f.code for f in rep.findings]
    assert "missing_required_section" in codes


def test_placeholder_section_flagged() -> None:
    payload = _minimal_ebp_spec()
    # mark safety placeholder
    for sec in payload["sections"]:
        if sec["section_id"] == "safety":
            sec["is_placeholder"] = True
            break
    rep = run_document_spec_invariants_validation(
        payload,
        case_inputs={"document_invariant_mode": "relaxed"},
    )
    assert any(f.code == "placeholder_or_empty_section" for f in rep.findings)


def test_identity_mismatch_title() -> None:
    payload = _minimal_ebp_spec()
    payload["title"] = "Generic neuromodulation compendium"
    payload["condition_slug"] = "parkinsons"
    rep = run_document_spec_invariants_validation(
        payload,
        case_inputs={"document_invariant_mode": "relaxed"},
    )
    assert any(f.code == "spec_identity_mismatch" for f in rep.findings)


def test_report_distinguishes_validators() -> None:
    payload = _minimal_ebp_spec()
    case = BenchmarkCase(
        id="inv",
        category="t",
        title="t",
        inputs={"document_invariant_mode": "relaxed", "min_document_references": 3},
        fixture_markdown="",
        expectations=BenchmarkExpectations(),
    )
    hr = HarnessResult(
        case_id=case.id,
        output_text="# x",
        document_spec=payload,
        metadata=HarnessMetadata(harness_id="generation_service", notes=[]),
    )
    ce = evaluate_case_result(case, "generation_service", hr)
    vids = {r.validator_id for r in ce.validator_reports}
    assert "structured_spec_validator" in vids
    assert "document_spec_invariants" in vids
    dim_names = {d.name for d in ce.dimensions}
    assert "structured_spec_quality" in dim_names
    assert "document_spec_invariants" in dim_names


def test_evaluator_dimension_for_native_codes() -> None:
    from autoagent_clinical.schemas import (
        FailureTaxonomy,
        Severity,
        ValidationFinding,
        ValidatorReport,
    )

    rep = ValidatorReport(
        validator_id="document_spec_invariants",
        findings=[
            ValidationFinding(
                code=FailureTaxonomy.MISSING_REQUIRED_SECTION.value,
                severity=Severity.HIGH,
                message="missing",
                reasons=[],
            )
        ],
    )
    dim = evaluate_document_spec_invariants([rep])
    assert dim.name == "document_spec_invariants"
    assert not dim.passed
