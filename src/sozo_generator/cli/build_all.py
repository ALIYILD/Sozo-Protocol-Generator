"""Build documents for all 15 conditions."""
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

build_all_app = typer.Typer(
    name="build-all",
    help="Build clinical documents for all conditions.",
    add_completion=False,
)

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]


def _parse_tiers(tier_str: str) -> list[Tier]:
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


@build_all_app.command("all")
def build_all(
    tier: str = typer.Option("both", "--tier", help="Tier: 'fellow', 'partners', or 'both'"),
    doc_type: str = typer.Option("all", "--doc-type", help="Document type slug or 'all'"),
    with_visuals: bool = typer.Option(True, "--with-visuals/--no-visuals", help="Include visual diagrams"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory"),
    skip_existing: bool = typer.Option(True, "--skip-existing/--no-skip-existing", help="Skip already-built conditions"),
    conditions: Optional[str] = typer.Option(None, "--conditions", help="Comma-separated subset of condition slugs"),
):
    """Build clinical documents for all 15 conditions."""
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    effective_output_dir = output_dir or settings.output_dir / "documents"
    visuals_dir = str(settings.visuals_dir)

    # Get all slugs from registry
    try:
        registry = get_registry()
        all_slugs = registry.list_slugs()
    except Exception as e:
        typer.echo(
            typer.style(
                f"Failed to load condition registry: {e}\nFalling back to built-in slug list.",
                fg=typer.colors.YELLOW,
            )
        )
        all_slugs = list(VALID_SLUGS)

    # Filter by --conditions if provided
    if conditions:
        requested = [s.strip() for s in conditions.split(",") if s.strip()]
        invalid = [s for s in requested if s not in all_slugs]
        if invalid:
            typer.echo(
                typer.style(
                    f"Unknown condition slug(s): {', '.join(invalid)}",
                    fg=typer.colors.YELLOW,
                )
            )
        all_slugs = [s for s in requested if s in all_slugs]
        if not all_slugs:
            typer.echo(typer.style("No valid condition slugs to build.", fg=typer.colors.RED))
            raise typer.Exit(code=1)

    tiers = _parse_tiers(tier)
    doc_types = _parse_doc_types(doc_type)

    total = len(all_slugs)
    typer.echo(
        typer.style(
            f"Building documents for {total} condition(s)...",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo(f"  Tiers:          {[t.value for t in tiers]}")
    typer.echo(f"  Doc types:      {len(doc_types)} type(s)")
    typer.echo(f"  Visuals:        {with_visuals}")
    typer.echo(f"  Skip existing:  {skip_existing}")
    typer.echo(f"  Output:         {effective_output_dir}")
    typer.echo("")

    success_count = 0
    failed: list[str] = []

    with typer.progressbar(all_slugs, label="Building", length=total) as progress:
        for slug in progress:
            # Skip-existing check: look for any output file for this condition
            if skip_existing:
                condition_out = Path(effective_output_dir) / slug.replace("_", " ").title().replace(" ", "_")
                if condition_out.exists() and any(condition_out.rglob("*.docx")):
                    success_count += 1
                    continue

            try:
                condition_obj = registry.get(slug)
                exporter = DocumentExporter(
                    output_dir=str(effective_output_dir),
                    with_visuals=with_visuals,
                )
                outputs = exporter.export_condition(
                    condition=condition_obj,
                    tiers=tiers,
                    doc_types=doc_types,
                    with_visuals=with_visuals,
                    visuals_dir=visuals_dir,
                )
                if outputs:
                    success_count += 1
                else:
                    typer.echo(
                        typer.style(f"\n  Warning: no outputs for '{slug}'", fg=typer.colors.YELLOW)
                    )
                    failed.append(slug)
            except Exception as e:
                typer.echo(
                    typer.style(f"\n  Failed '{slug}': {e}", fg=typer.colors.RED)
                )
                failed.append(slug)

    typer.echo("")
    typer.echo(
        typer.style(
            f"Built {success_count}/{total} conditions successfully.",
            fg=typer.colors.GREEN if not failed else typer.colors.YELLOW,
        )
    )
    if failed:
        typer.echo(
            typer.style(
                f"Failed conditions: {', '.join(failed)}",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)
