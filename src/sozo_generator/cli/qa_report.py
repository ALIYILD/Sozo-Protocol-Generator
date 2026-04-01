"""Run QA checks and generate review report."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer

try:
    from ..core.enums import DocumentType, Tier
    from ..core.settings import SozoSettings
    from ..conditions.registry import get_registry
    from ..schemas.review import ConditionQAReport, DocumentQAResult
except ImportError as e:
    typer.echo(
        typer.style(
            f"Import error: {e}\n"
            "Ensure sozo_generator is installed and all dependencies are available.",
            fg=typer.colors.RED,
        )
    )
    raise SystemExit(1)

qa_app = typer.Typer(
    name="qa",
    help="Run QA checks and generate review reports.",
    add_completion=False,
)

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]

MIN_FILE_SIZE = 1000  # bytes

# Expected documents per tier/type combination (mirrors exporter logic)
EXPECTED_DOCUMENTS = [
    (Tier.FELLOW, DocumentType.CLINICAL_EXAM),
    (Tier.FELLOW, DocumentType.PHENOTYPE_CLASSIFICATION),
    (Tier.FELLOW, DocumentType.RESPONDER_TRACKING),
    (Tier.FELLOW, DocumentType.PSYCH_INTAKE),
    (Tier.FELLOW, DocumentType.HANDBOOK),
    (Tier.FELLOW, DocumentType.ALL_IN_ONE_PROTOCOL),
    (Tier.FELLOW, DocumentType.EVIDENCE_BASED_PROTOCOL),
    (Tier.PARTNERS, DocumentType.CLINICAL_EXAM),
    (Tier.PARTNERS, DocumentType.PHENOTYPE_CLASSIFICATION),
    (Tier.PARTNERS, DocumentType.RESPONDER_TRACKING),
    (Tier.PARTNERS, DocumentType.PSYCH_INTAKE),
    (Tier.PARTNERS, DocumentType.NETWORK_ASSESSMENT),
    (Tier.PARTNERS, DocumentType.HANDBOOK),
    (Tier.PARTNERS, DocumentType.ALL_IN_ONE_PROTOCOL),
    (Tier.PARTNERS, DocumentType.EVIDENCE_BASED_PROTOCOL),
]

FILENAME_MAP = {
    DocumentType.CLINICAL_EXAM: "Clinical_Examination_Checklist_{tier}.docx",
    DocumentType.PHENOTYPE_CLASSIFICATION: "Phenotype_Classification_{tier}.docx",
    DocumentType.RESPONDER_TRACKING: "Responder_Tracking_{tier}.docx",
    DocumentType.PSYCH_INTAKE: "Psychological_Intake_PRS_Baseline_{tier}.docx",
    DocumentType.NETWORK_ASSESSMENT: "6Network_Bedside_Assessment_{tier}.docx",
    DocumentType.HANDBOOK: "SOZO_Clinical_Handbook_{tier}.docx",
    DocumentType.ALL_IN_ONE_PROTOCOL: "All_In_One_Protocol_{tier}.docx",
    DocumentType.EVIDENCE_BASED_PROTOCOL: "Evidence_Based_Protocol_{tier}.docx",
}

SUBFOLDER_MAP = {
    DocumentType.CLINICAL_EXAM: "Assessments",
    DocumentType.PHENOTYPE_CLASSIFICATION: "Assessments",
    DocumentType.RESPONDER_TRACKING: "Assessments",
    DocumentType.PSYCH_INTAKE: "Assessments",
    DocumentType.NETWORK_ASSESSMENT: "Assessments",
    DocumentType.HANDBOOK: "Handbook",
    DocumentType.ALL_IN_ONE_PROTOCOL: "Protocols",
    DocumentType.EVIDENCE_BASED_PROTOCOL: "Protocols",
}

REQUIRED_CONDITION_FIELDS = ["display_name", "network_profiles", "phenotypes", "protocols"]


def _get_doc_path(documents_dir: Path, slug: str, tier: Tier, doc_type: DocumentType) -> Path:
    """Compute expected path for a document (matches DocumentRenderer output layout)."""
    tier_cap = tier.value.capitalize()
    filename = FILENAME_MAP.get(doc_type, f"{doc_type.value}_{tier_cap}.docx").format(tier=tier_cap)
    # Actual layout: outputs/documents/{slug}/{tier_lower}/{Filename}.docx
    return documents_dir / slug / tier.value / filename


def _check_condition_schema(condition_obj) -> list[str]:
    """Return list of missing required fields in the condition schema."""
    missing = []
    if isinstance(condition_obj, dict):
        for field in REQUIRED_CONDITION_FIELDS:
            if not condition_obj.get(field):
                missing.append(field)
    else:
        for field in REQUIRED_CONDITION_FIELDS:
            if not getattr(condition_obj, field, None):
                missing.append(field)
    return missing


def _run_qa_for_slug(slug: str, documents_dir: Path) -> ConditionQAReport:
    """Run QA checks for a single condition slug."""
    registry = get_registry()
    try:
        condition_obj = registry.get(slug)
    except Exception as e:
        return ConditionQAReport(
            condition_slug=slug,
            condition_name=slug,
            generated_at=datetime.now().isoformat(),
            total_documents=0,
            passed_documents=0,
            recommendations=[f"Could not load condition from registry: {e}"],
            ready_for_clinical_review=False,
        )

    condition_name = (
        condition_obj.get("display_name", slug)
        if isinstance(condition_obj, dict)
        else getattr(condition_obj, "display_name", slug)
    )

    doc_results: list[DocumentQAResult] = []
    missing_schema_fields = _check_condition_schema(condition_obj)
    recommendations: list[str] = []

    if missing_schema_fields:
        recommendations.append(
            f"Condition schema missing fields: {', '.join(missing_schema_fields)}"
        )

    for tier, doc_type in EXPECTED_DOCUMENTS:
        doc_path = _get_doc_path(documents_dir, slug, tier, doc_type)
        exists = doc_path.exists()
        size_ok = False
        notes: list[str] = []

        if exists:
            size = doc_path.stat().st_size
            size_ok = size >= MIN_FILE_SIZE
            if not size_ok:
                notes.append(f"File too small ({size} bytes, minimum {MIN_FILE_SIZE})")
        else:
            notes.append(f"File not found: {doc_path}")

        passed = exists and size_ok
        completeness = 1.0 if passed else 0.0

        doc_result = DocumentQAResult(
            document_type=doc_type.value,
            tier=tier.value,
            condition_slug=slug,
            completeness_score=completeness,
            evidence_coverage=0.0,
            has_placeholders=False,
            missing_sections=[] if passed else [str(doc_path.name)],
            passed=passed,
            notes=notes,
        )
        doc_results.append(doc_result)

    total_docs = len(doc_results)
    passed_docs = sum(1 for d in doc_results if d.passed)
    overall_completeness = passed_docs / total_docs if total_docs > 0 else 0.0

    flagged = [d for d in doc_results if not d.passed]
    if flagged:
        recommendations.append(
            f"{len(flagged)} document(s) missing or too small."
        )

    ready = overall_completeness >= 0.8 and not missing_schema_fields

    return ConditionQAReport(
        condition_slug=slug,
        condition_name=condition_name,
        generated_at=datetime.now().isoformat(),
        total_documents=total_docs,
        passed_documents=passed_docs,
        overall_completeness=overall_completeness,
        overall_evidence_coverage=0.0,
        document_results=doc_results,
        recommendations=recommendations,
        ready_for_clinical_review=ready,
    )


@qa_app.command("report")
def qa_report(
    condition: str = typer.Option(..., "--condition", help="Condition slug or 'all'"),
    output_path: Optional[Path] = typer.Option(None, "--output", help="Output path for the report"),
    format: str = typer.Option("json", "--format", help="Output format: 'json' or 'markdown'"),
):
    """Run QA checks for a condition and generate a review report."""
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    documents_dir = settings.output_dir / "documents"

    if format not in ("json", "markdown"):
        typer.echo(typer.style(f"Invalid format '{format}'. Use 'json' or 'markdown'.", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Determine which slugs to check
    if condition.lower() == "all":
        try:
            registry = get_registry()
            slugs = registry.list_slugs()
        except Exception:
            slugs = list(VALID_SLUGS)
    else:
        slugs = [condition]

    typer.echo(
        typer.style(
            f"Running QA checks for {len(slugs)} condition(s)...",
            fg=typer.colors.CYAN,
        )
    )

    reports: list[ConditionQAReport] = []
    for slug in slugs:
        typer.echo(f"  Checking: {slug}")
        report = _run_qa_for_slug(slug, documents_dir)
        reports.append(report)

    # Build output
    if format == "json":
        output_data = [r.model_dump() for r in reports]
        output_str = json.dumps(output_data if len(reports) > 1 else output_data[0], indent=2, ensure_ascii=False)
    else:
        lines = ["# SOZO QA Report\n"]
        for r in reports:
            status_icon = "PASS" if r.ready_for_clinical_review else "FAIL"
            lines.append(f"## {r.condition_name} ({r.condition_slug}) — {status_icon}")
            lines.append(f"- Generated: {r.generated_at}")
            lines.append(f"- Documents: {r.passed_documents}/{r.total_documents} passed")
            lines.append(f"- Completeness: {r.overall_completeness:.0%}")
            lines.append(f"- Ready for clinical review: {r.ready_for_clinical_review}")
            if r.recommendations:
                lines.append("### Recommendations")
                for rec in r.recommendations:
                    lines.append(f"- {rec}")
            missing = [d for d in r.document_results if not d.passed]
            if missing:
                lines.append("### Missing/Failed Documents")
                for d in missing:
                    lines.append(f"- [{d.tier}] {d.document_type}: {'; '.join(d.notes)}")
            lines.append("")
        output_str = "\n".join(lines)

    if output_path:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(output_str, encoding="utf-8")
            typer.echo("")
            typer.echo(typer.style(f"Report written to: {output_path}", fg=typer.colors.GREEN))
        except Exception as e:
            typer.echo(typer.style(f"Failed to write report: {e}", fg=typer.colors.RED))
            raise typer.Exit(code=1)
    else:
        typer.echo("")
        typer.echo(output_str)

    # Summary
    typer.echo("")
    for r in reports:
        status_color = typer.colors.GREEN if r.ready_for_clinical_review else typer.colors.RED
        status_label = "READY" if r.ready_for_clinical_review else "NOT READY"
        typer.echo(
            typer.style(f"  [{status_label}] ", fg=status_color)
            + f"{r.condition_slug}: {r.passed_documents}/{r.total_documents} docs passed "
            + f"({r.overall_completeness:.0%} complete)"
        )

    flagged_conditions = [r for r in reports if not r.ready_for_clinical_review]
    if flagged_conditions:
        typer.echo("")
        typer.echo(
            typer.style(
                f"{len(flagged_conditions)} condition(s) flagged: "
                + ", ".join(r.condition_slug for r in flagged_conditions),
                fg=typer.colors.YELLOW,
            )
        )
