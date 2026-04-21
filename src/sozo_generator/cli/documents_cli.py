"""Deterministic long-form document production commands."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

from ..generation.document_production import (
    generate_condition_documents,
    DEFAULT_DOC_TYPES,
)

documents_app = typer.Typer(
    name="documents",
    help="Generate Assessment/Protocol/Handbook variants (Fellow/Partners).",
    add_completion=False,
)


@documents_app.command("generate")
def generate(
    condition: str = typer.Option(..., "--condition", help="Condition slug (e.g. parkinsons)"),
    doc_type: str = typer.Option(
        "all",
        "--doc-type",
        help="assessment|protocol|handbook|all",
    ),
    tier: str = typer.Option(
        "both",
        "--tier",
        help="fellow|partners|both",
    ),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory"),
    pdf: bool = typer.Option(False, "--pdf/--no-pdf", help="Also export PDF (if supported)"),
    visuals: bool = typer.Option(False, "--visuals/--no-visuals", help="Generate visuals (slower)"),
    qa: bool = typer.Option(True, "--qa/--no-qa", help="Run QA checks during generation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write artifacts"),
    validate_only: bool = typer.Option(False, "--validate-only", help="Assemble and validate without rendering"),
):
    """Generate the 3×2 document set for one condition (or a subset)."""
    doc_map = {
        "assessment": ("clinical_exam",),
        "protocol": ("evidence_based_protocol",),
        "handbook": ("handbook",),
        "all": DEFAULT_DOC_TYPES,
    }
    if doc_type not in doc_map:
        raise typer.BadParameter("doc-type must be one of: assessment, protocol, handbook, all")

    tiers = ("fellow", "partners") if tier == "both" else (tier,)
    if tier not in ("fellow", "partners", "both"):
        raise typer.BadParameter("tier must be one of: fellow, partners, both")

    run = generate_condition_documents(
        condition_slug=condition,
        doc_types=tuple(doc_map[doc_type]),
        tiers=tuple(tiers),
        output_dir=str(output_dir) if output_dir else None,
        with_pdf=pdf,
        with_visuals=visuals,
        with_qa=qa,
        dry_run=dry_run,
        validate_only=validate_only,
    )

    typer.echo(f"Build: {run.build_id}")
    if run.manifest_path:
        typer.echo(f"Manifest: {run.manifest_path}")
    for r in run.results:
        status = "OK" if r.success else "FAIL"
        typer.echo(f"- [{status}] {r.tier}/{r.doc_type}  {r.output_path or ''}".rstrip())
        if r.error:
            typer.echo(f"    error: {r.error}")
        if r.qa_issues:
            for q in r.qa_issues[:5]:
                typer.echo(f"    qa: {q}")


@documents_app.command("generate-batch")
def generate_batch(
    all_conditions: bool = typer.Option(True, "--all-conditions", help="Generate for all known knowledge conditions"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory"),
    pdf: bool = typer.Option(False, "--pdf/--no-pdf", help="Also export PDF (if supported)"),
    visuals: bool = typer.Option(False, "--visuals/--no-visuals", help="Generate visuals (slower)"),
    qa: bool = typer.Option(True, "--qa/--no-qa", help="Run QA checks during generation"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not write artifacts"),
):
    """Generate the 3×2 document set for all knowledge conditions."""
    if not all_conditions:
        raise typer.BadParameter("Only --all-conditions is supported right now")

    from ..knowledge.base import KnowledgeBase

    kb = KnowledgeBase()
    kb.load_all()
    slugs = kb.list_conditions()
    typer.echo(f"Conditions: {len(slugs)}")

    for slug in slugs:
        typer.echo(f"\n== {slug} ==")
        run = generate_condition_documents(
            condition_slug=slug,
            output_dir=str(output_dir) if output_dir else None,
            with_pdf=pdf,
            with_visuals=visuals,
            with_qa=qa,
            dry_run=dry_run,
        )
        ok = sum(1 for r in run.results if r.success)
        typer.echo(f"Build: {run.build_id}  ({ok}/{len(run.results)} ok)")


@documents_app.command("validate")
def validate(
    condition: Optional[str] = typer.Option(None, "--condition", help="Condition slug to validate"),
):
    """Validate canonical assembly for the 3×2 set (no rendering)."""
    from ..knowledge.base import KnowledgeBase

    kb = KnowledgeBase()
    kb.load_all()
    slugs = [condition] if condition else kb.list_conditions()

    failures = 0
    for slug in slugs:
        run = generate_condition_documents(
            condition_slug=slug,
            with_visuals=False,
            with_pdf=False,
            with_qa=False,
            validate_only=True,
        )
        bad = [r for r in run.results if not r.success]
        if bad:
            failures += 1
            typer.echo(f"[FAIL] {slug}: {len(bad)} failure(s)")
            for r in bad:
                typer.echo(f"  - {r.tier}/{r.doc_type}: {r.error}")
        else:
            typer.echo(f"[OK] {slug}")

    raise typer.Exit(code=1 if failures else 0)

