"""Phase 3: structured DocumentSpec path for AutoAgent-Clinical."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from autoagent_clinical.evaluators import evaluate_structured_spec
from autoagent_clinical.harnesses.generation_service_harness import GenerationServiceHarness
from autoagent_clinical.normalize import document_spec_to_benchmark_markdown
from autoagent_clinical.runner import evaluate_case_result, run_suite
from autoagent_clinical.schemas import BenchmarkCase, BenchmarkExpectations, BenchmarkSuite
from autoagent_clinical.validators import run_structured_spec_validation


def test_document_spec_to_markdown_includes_headings() -> None:
    from sozo_generator.schemas.documents import DocumentSpec, SectionContent
    from sozo_generator.core.enums import DocumentType, Tier

    spec = DocumentSpec(
        document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
        tier=Tier.FELLOW,
        condition_slug="parkinsons",
        condition_name="PD",
        title="Test protocol",
        audience="Fellow",
        sections=[
            SectionContent(
                section_id="a",
                title="Overview",
                content="Discuss adjunct care. PMID: 11111111",
            )
        ],
    )
    md = document_spec_to_benchmark_markdown(spec)
    assert "# Test protocol" in md
    assert "## Overview" in md
    assert "PMID: 11111111" in md


def test_structured_spec_validator_malformed_dict() -> None:
    report = run_structured_spec_validation(
        {"not_a_real_spec": True},
        case_inputs={"require_document_spec_sections": 1},
    )
    assert report.findings
    assert any(f.code == "malformed_structured_output" for f in report.findings)


def test_structured_spec_evaluator_neutral_when_no_spec() -> None:
    from autoagent_clinical.schemas import ValidatorReport

    dim = evaluate_structured_spec(
        [ValidatorReport(validator_id="structured_spec_validator", findings=[])]
    )
    assert dim.passed
    assert dim.name == "structured_spec_quality"


@pytest.mark.integration
def test_live_harness_uses_structured_source_when_canonical(tmp_path: Path) -> None:
    from sozo_generator.generation.service import GenerationService

    def factory():
        return GenerationService(
            output_dir=str(tmp_path),
            with_visuals=False,
            with_qa=False,
        )

    h = GenerationServiceHarness(service_factory=factory)
    case = BenchmarkCase(
        id="live_struct",
        category="generation_adapter",
        title="t",
        inputs={
            "condition": "parkinsons",
            "tier": "fellow",
            "doc_type": "evidence_based_protocol",
            "relaxed_citation_check": True,
        },
        fixture_markdown="# stub",
        expectations=BenchmarkExpectations(),
    )
    res = h.run(case)
    if res.metadata.structured_source == "failure":
        pytest.skip(f"generation unavailable: {res.metadata.notes[:2]}")
    assert res.metadata.structured_source == "document_spec"
    assert res.document_spec is not None
    assert "sections" in res.document_spec
    assert "#" in res.output_text


def test_benchmark_text_source_docx_only(tmp_path: Path) -> None:
    from sozo_generator.generation.service import GenerationService

    def factory():
        return GenerationService(
            output_dir=str(tmp_path),
            with_visuals=False,
            with_qa=False,
        )

    h = GenerationServiceHarness(service_factory=factory)
    case = BenchmarkCase(
        id="docx_only",
        category="generation_adapter",
        title="t",
        inputs={
            "condition": "parkinsons",
            "tier": "fellow",
            "doc_type": "evidence_based_protocol",
            "benchmark_text_source": "docx_only",
            "relaxed_citation_check": True,
        },
        fixture_markdown="# stub",
        expectations=BenchmarkExpectations(),
    )
    res = h.run(case)
    if res.metadata.structured_source == "failure":
        pytest.skip(f"generation unavailable: {res.metadata.notes[:2]}")
    assert res.metadata.structured_source == "docx_extract"
    assert res.document_spec is None
    assert res.assembly_provenance is not None or "output_path=" in " ".join(
        res.metadata.notes
    )


def test_structured_only_unknown_condition_surfaces_failure() -> None:
    from sozo_generator.generation.service import GenerationService

    h = GenerationServiceHarness(service_factory=lambda: GenerationService(with_visuals=False, with_qa=False))
    case = BenchmarkCase(
        id="st_only_bad",
        category="generation_adapter",
        title="t",
        inputs={
            "condition": "__no_such_autoagent_slug__",
            "tier": "fellow",
            "doc_type": "evidence_based_protocol",
            "benchmark_text_source": "structured_only",
        },
        fixture_markdown="x",
        expectations=BenchmarkExpectations(),
    )
    res = h.run(case)
    assert res.metadata.structured_source == "failure"
    assert "# Generation failed" in res.output_text


def test_magicmock_still_docx_path_no_assembly() -> None:
    from sozo_generator.generation.service import GenerationResult

    def factory():
        svc = MagicMock()
        svc.generate.return_value = [
            GenerationResult(
                condition_slug="parkinsons",
                tier="fellow",
                doc_type="evidence_based_protocol",
                success=False,
                error="no file",
            )
        ]
        return svc

    h = GenerationServiceHarness(service_factory=factory)
    case = BenchmarkCase(
        id="mock",
        category="x",
        title="t",
        inputs={"condition": "parkinsons", "tier": "fellow", "doc_type": "evidence_based_protocol"},
        fixture_markdown="x",
        expectations=BenchmarkExpectations(),
    )
    res = h.run(case)
    # MagicMock is not GenerationService → no structured path; uses generate()
    assert res.document_spec is None


def test_benchmark_run_report_top_level_stable() -> None:
    from autoagent_clinical.schemas import BenchmarkRunReport

    keys = set(BenchmarkRunReport.model_fields.keys())
    assert {"run_id", "summary", "case_results", "harness_id", "suite"}.issubset(keys)


def test_runner_preserves_report_fields_with_document_spec() -> None:
    from sozo_generator.generation.service import GenerationService

    svc = GenerationService(with_visuals=False, with_qa=False)
    assembled = svc.assemble_canonical_document(
        "parkinsons", "evidence_based_protocol", "fellow"
    )
    if not assembled.ok:
        pytest.skip("KB not available for integration check")
    spec = assembled.spec
    assert spec is not None
    case = BenchmarkCase(
        id="eval_struct",
        category="x",
        title="t",
        inputs={"relaxed_citation_check": True},
        fixture_markdown="",
        expectations=BenchmarkExpectations(),
    )
    from autoagent_clinical.schemas import HarnessMetadata, HarnessResult

    hr = HarnessResult(
        case_id=case.id,
        output_text=document_spec_to_benchmark_markdown(spec),
        document_spec=spec.model_dump(mode="json"),
        metadata=HarnessMetadata(harness_id="generation_service", notes=[]),
    )
    ce = evaluate_case_result(case, "generation_service", hr)
    assert ce.case_id == case.id
    assert any(d.name == "structured_spec_quality" for d in ce.dimensions)
    names = {r.validator_id for r in ce.validator_reports}
    assert "structured_spec_validator" in names
    assert "document_spec_invariants" in names


def test_run_suite_json_roundtrip_keys() -> None:
    suite = BenchmarkSuite(
        cases=[
            BenchmarkCase(
                id="k",
                category="c",
                title="t",
                inputs={},
                fixture_markdown="# H\n\nbody",
                expectations=BenchmarkExpectations(),
            )
        ]
    )
    report = run_suite(suite, "baseline_fixture")
    data = report.model_dump()
    assert set(data.keys()) >= {"run_id", "summary", "case_results", "harness_id"}
