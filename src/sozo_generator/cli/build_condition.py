"""Build documents for a single condition."""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer

try:
    from ..core.enums import Tier, DocumentType
    from ..core.settings import SozoSettings
    from ..conditions.registry import get_registry
    from ..docx.exporter import DocumentExporter
except ImportError as e:
    typer.echo(
        typer.style(
            f"Import error: {e}\n"
            "Ensure sozo_generator is installed and all dependencies are available.",
            fg=typer.colors.RED,
        )
    )
    raise SystemExit(1)

build_app = typer.Typer(
    name="build",
    help="Build clinical documents for conditions.",
    add_completion=False,
)

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]


def _parse_tiers(tier_str: str) -> list[Tier]:
    """Convert tier string to list of Tier enums."""
    tier_str = tier_str.lower().strip()
    if tier_str == "both":
        return [Tier.FELLOW, Tier.PARTNERS]
    try:
        return [Tier(tier_str)]
    except ValueError:
        typer.echo(
            typer.style(
                f"Invalid tier '{tier_str}'. Must be 'fellow', 'partners', or 'both'.",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)


def _parse_doc_types(doc_type_str: str) -> list[DocumentType]:
    """Convert doc-type string to list of DocumentType enums."""
    doc_type_str = doc_type_str.lower().strip()
    if doc_type_str == "all":
        return list(DocumentType)
    try:
        return [DocumentType(doc_type_str)]
    except ValueError:
        valid = ", ".join(dt.value for dt in DocumentType)
        typer.echo(
            typer.style(
                f"Invalid doc-type '{doc_type_str}'. Valid values: {valid}, all",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)


@build_app.command("condition")
def build_condition(
    condition: str = typer.Option(..., "--condition", help="Condition slug (e.g. parkinsons)"),
    tier: str = typer.Option("both", "--tier", help="Tier: 'fellow', 'partners', or 'both'"),
    doc_type: str = typer.Option("all", "--doc-type", help="Document type slug or 'all'"),
    with_visuals: bool = typer.Option(True, "--with-visuals/--no-visuals", help="Include visual diagrams"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory"),
):
    """Build clinical documents for a single condition."""
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Resolve output directory
    effective_output_dir = output_dir or settings.output_dir / "documents"
    visuals_dir = str(settings.visuals_dir)

    # Load condition from registry
    try:
        registry = get_registry()
        condition_obj = registry.get(condition)
    except Exception as e:
        typer.echo(typer.style(f"Condition '{condition}' not found: {e}", fg=typer.colors.RED))
        typer.echo(
            typer.style(
                f"Valid slugs: {', '.join(VALID_SLUGS)}",
                fg=typer.colors.YELLOW,
            )
        )
        raise typer.Exit(code=1)

    # Parse tiers and doc types
    tiers = _parse_tiers(tier)
    doc_types = _parse_doc_types(doc_type)

    typer.echo(
        typer.style(
            f"Building documents for: {condition}",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo(f"  Tiers:     {[t.value for t in tiers]}")
    typer.echo(f"  Doc types: {[dt.value for dt in doc_types]}")
    typer.echo(f"  Visuals:   {with_visuals}")
    typer.echo(f"  Output:    {effective_output_dir}")

    try:
        exporter = DocumentExporter(output_dir=str(effective_output_dir), with_visuals=with_visuals)
        outputs = exporter.export_condition(
            condition=condition_obj,
            tiers=tiers,
            doc_types=doc_types,
            with_visuals=with_visuals,
            visuals_dir=visuals_dir,
        )
    except Exception as e:
        typer.echo(typer.style(f"Export failed: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    if not outputs:
        typer.echo(typer.style("No documents were generated.", fg=typer.colors.YELLOW))
        raise typer.Exit(code=1)

    typer.echo("")
    for key, path in outputs.items():
        typer.echo(typer.style(f"  [OK] ", fg=typer.colors.GREEN) + str(path))

    typer.echo("")
    typer.echo(
        typer.style(
            f"Successfully built {len(outputs)} document(s) for '{condition}'.",
            fg=typer.colors.GREEN,
        )
    )
