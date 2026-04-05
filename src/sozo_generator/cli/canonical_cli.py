"""
canonical CLI — long-document pipeline commands for SOZO Generator.

Commands:
  canonical generate   Full end-to-end document generation
  canonical plan       Build and print/save a document blueprint
  canonical validate   Run QA validators on a canonical document JSON
  canonical export     Export a canonical document JSON to DOCX/HTML/PDF
  canonical demo       Quick end-to-end demo for a condition
"""
import json
import os
from typing import Optional

import typer

app = typer.Typer(
    name="canonical",
    help="Canonical long-document pipeline (blueprints → sections → assembly → QA → export)",
)


@app.command("generate")
def generate_canonical_document(
    condition: str = typer.Argument(..., help="Condition slug (e.g. parkinsons, depression)"),
    variant: str = typer.Option("partners", "--variant", "-v", help="fellow | partners"),
    document_type: str = typer.Option(
        "handbook", "--type", "-t", help="handbook | protocol | assessment | all_in_one"
    ),
    pages: int = typer.Option(60, "--pages", "-p", help="Target page count"),
    skip_assets: bool = typer.Option(False, "--skip-assets", help="Skip figure/chart generation"),
    skip_pdf: bool = typer.Option(True, "--skip-pdf", help="Skip PDF export"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o", help="Output directory"),
) -> None:
    """Generate a canonical long-form document end-to-end."""
    from sozo_generator.orchestration.document_orchestrator import DocumentOrchestrator

    typer.echo(f"Generating {document_type} for {condition} ({variant})...")

    orchestrator = DocumentOrchestrator(
        skip_assets=skip_assets,
        skip_pdf=skip_pdf,
    )
    result = orchestrator.generate(
        condition_slug=condition,
        variant=variant,
        document_type=document_type,
        target_page_count=pages,
        output_dir=output_dir,
    )

    if result.success:
        typer.echo(typer.style("✓ Generation complete", fg=typer.colors.GREEN))
        typer.echo(f"  Sections generated: {result.sections_generated}")
        typer.echo(f"  Assets generated:   {result.assets_generated}")
        typer.echo(f"  QA passed:          {result.qa_passed}")
        typer.echo(f"  Duration:           {result.duration_seconds:.1f}s")
        for fmt, path in result.output_paths.items():
            typer.echo(f"  {fmt.upper()}: {path}")
    else:
        typer.echo(typer.style("✗ Generation failed", fg=typer.colors.RED), err=True)
        for err in result.errors:
            typer.echo(f"  ERROR: {err}", err=True)
        for warn in result.warnings:
            typer.echo(f"  WARN:  {warn}")
        raise typer.Exit(1)


@app.command("plan")
def plan_document(
    condition: str = typer.Argument(..., help="Condition slug"),
    variant: str = typer.Option("partners", "--variant", "-v"),
    document_type: str = typer.Option("handbook", "--type", "-t"),
    pages: int = typer.Option(60, "--pages", "-p"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save blueprint JSON to path"),
) -> None:
    """Build and display a document blueprint without generating content."""
    from sozo_generator.planning.document_blueprint_builder import DocumentBlueprintBuilder

    typer.echo(f"Planning {document_type} for {condition} ({variant})...")

    builder = DocumentBlueprintBuilder()
    blueprint = builder.build(
        condition_slug=condition,
        variant=variant,
        document_type=document_type,
        target_page_count=pages,
    )

    typer.echo(f"\nBlueprint: {blueprint.blueprint_id}")
    typer.echo(f"Title:     {blueprint.title}")
    typer.echo(f"Sections:  {len(blueprint.sections)}")
    typer.echo(f"Target:    {blueprint.target_page_count} pages / ~{blueprint.target_word_count:,} words\n")

    for i, sec in enumerate(blueprint.sections, 1):
        indent = "  "
        typer.echo(f"{indent}{i:2}. {sec.title}")
        typer.echo(f"{indent}    words={sec.target_word_count}, assets={len(sec.required_asset_ids)}")
        for sub in sec.subsections:
            typer.echo(f"{indent}    └─ {sub.title} ({sub.target_word_count}w)")

    if output:
        path = builder.save(blueprint, os.path.dirname(output) or ".")
        typer.echo(f"\nBlueprint saved: {path}")


@app.command("render-assets")
def render_document_assets(
    condition: str = typer.Argument(..., help="Condition slug (e.g. parkinsons)"),
    variant: str = typer.Option("partners", "--variant", "-v", help="fellow | partners"),
    document_type: str = typer.Option("handbook", "--type", "-t", help="handbook | protocol | assessment | all_in_one"),
) -> None:
    """Render all tables, figures, and charts for a condition without generating text."""
    from sozo_generator.orchestration.document_orchestrator import DocumentOrchestrator

    typer.echo(f"Rendering assets for {condition} ({variant}/{document_type})...")

    orchestrator = DocumentOrchestrator()
    try:
        summary = orchestrator.rebuild_assets_only(
            condition_slug=condition,
            variant=variant,
            document_type=document_type,
        )
    except Exception as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)

    if summary.get("success"):
        typer.echo(typer.style("Asset render complete", fg=typer.colors.GREEN))
        typer.echo(f"  Total:     {summary.get('total', 'N/A')}")
        typer.echo(f"  Generated: {summary.get('generated', 'N/A')}")
        typer.echo(f"  Failed:    {summary.get('failed', 'N/A')}")
    else:
        typer.echo(f"Error: {summary.get('error', 'unknown')}", err=True)
        raise typer.Exit(1)


@app.command("assemble")
def assemble_document(
    canonical_doc: str = typer.Argument(..., help="Path to canonical document JSON"),
) -> None:
    """Re-run export from an existing canonical document JSON (no text regeneration)."""
    from sozo_generator.orchestration.document_orchestrator import DocumentOrchestrator

    if not os.path.exists(canonical_doc):
        typer.echo(f"Error: File not found: {canonical_doc}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Re-assembling from {canonical_doc}...")

    orchestrator = DocumentOrchestrator()
    result = orchestrator.reassemble(canonical_doc)

    if result.success:
        typer.echo(typer.style("Re-assembly complete", fg=typer.colors.GREEN))
        for fmt, path in result.output_paths.items():
            typer.echo(f"  {fmt.upper()}: {path}")
        if result.warnings:
            for w in result.warnings:
                typer.echo(f"  WARN: {w}")
    else:
        typer.echo("Error: Re-assembly failed", err=True)
        for err in result.errors:
            typer.echo(f"  {err}", err=True)
        raise typer.Exit(1)


@app.command("validate")
def validate_document(
    canonical_doc: str = typer.Argument(..., help="Path to canonical document JSON"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Save QA report JSON"),
) -> None:
    """Run all QA validators on a canonical document."""
    from sozo_generator.schemas.canonical import CanonicalDocument
    from sozo_generator.qa.validators.document_qa_runner import DocumentQARunner

    if not os.path.exists(canonical_doc):
        typer.echo(f"File not found: {canonical_doc}", err=True)
        raise typer.Exit(1)

    with open(canonical_doc, encoding="utf-8") as f:
        document = CanonicalDocument.model_validate(json.load(f))

    runner = DocumentQARunner()
    report = runner.run(document)

    typer.echo(runner.to_human_readable(report))

    if output:
        with open(output, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        typer.echo(f"\nQA report saved: {output}")

    if not report.overall_passed:
        raise typer.Exit(1)


@app.command("export")
def export_document(
    canonical_doc: str = typer.Argument(..., help="Path to canonical document JSON"),
    formats: str = typer.Option("docx,html", "--formats", "-f", help="docx,html,pdf"),
    output_dir: Optional[str] = typer.Option(None, "--output-dir", "-o"),
) -> None:
    """Export a canonical document to DOCX/HTML/PDF."""
    from sozo_generator.orchestration.document_orchestrator import DocumentOrchestrator

    if not os.path.exists(canonical_doc):
        typer.echo(f"File not found: {canonical_doc}", err=True)
        raise typer.Exit(1)

    fmt_list = [f.strip() for f in formats.split(",")]
    orchestrator = DocumentOrchestrator()
    result = orchestrator.export_only(canonical_doc, formats=fmt_list)

    for fmt, path in result.output_paths.items():
        typer.echo(f"{fmt.upper()}: {path}")

    if result.errors:
        for err in result.errors:
            typer.echo(f"Error: {err}", err=True)
        raise typer.Exit(1)


@app.command("demo")
def run_demo(
    condition: str = typer.Option("parkinsons", "--condition", "-c"),
    variant: str = typer.Option("partners", "--variant", "-v"),
) -> None:
    """
    Run a complete end-to-end demo for a condition.
    Uses document_type='protocol' (faster than handbook) and skips assets.
    """
    from sozo_generator.orchestration.document_orchestrator import DocumentOrchestrator

    typer.echo(f"\n{'='*60}")
    typer.echo(f"  SOZO Canonical Pipeline Demo")
    typer.echo(f"  Condition: {condition}  |  Variant: {variant}")
    typer.echo(f"{'='*60}\n")

    orchestrator = DocumentOrchestrator(skip_assets=True, skip_pdf=True)
    result = orchestrator.generate(
        condition_slug=condition,
        variant=variant,
        document_type="protocol",
        target_page_count=30,
    )

    typer.echo(f"\n{'='*60}")
    status = typer.style("PASS", fg=typer.colors.GREEN) if result.success else typer.style("FAIL", fg=typer.colors.RED)
    typer.echo(f"  Result: {status}")
    typer.echo(f"  Duration: {result.duration_seconds:.1f}s")
    typer.echo(f"  Sections: {result.sections_generated}")
    typer.echo(f"  QA passed: {result.qa_passed}")
    if result.output_paths:
        typer.echo("  Outputs:")
        for fmt, path in result.output_paths.items():
            typer.echo(f"    {fmt}: {path}")
    if result.warnings:
        typer.echo(f"  Warnings: {len(result.warnings)}")
        for w in result.warnings[:3]:
            typer.echo(f"    - {w}")
    typer.echo(f"{'='*60}\n")
