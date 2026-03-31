"""Render visual figures for a condition."""
from pathlib import Path
from typing import Optional

import typer

try:
    from ..core.settings import SozoSettings
    from ..conditions.registry import get_registry
except ImportError as e:
    typer.echo(
        typer.style(
            f"Import error: {e}\n"
            "Ensure sozo_generator is installed and all dependencies are available.",
            fg=typer.colors.RED,
        )
    )
    raise SystemExit(1)

visuals_app = typer.Typer(
    name="visuals",
    help="Render visual figures for conditions.",
    add_completion=False,
)

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]


def _import_visuals_exporter():
    """Lazily import VisualsExporter with a helpful error on failure."""
    try:
        from ..visuals.exporters import VisualsExporter  # type: ignore
        return VisualsExporter
    except ImportError as e:
        typer.echo(
            typer.style(
                f"Could not import VisualsExporter: {e}\n"
                "Ensure the visuals module is installed (matplotlib, numpy required).",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)


@visuals_app.command("render")
def render_visuals(
    condition: str = typer.Option(..., "--condition", help="Condition slug or 'all'"),
    force: bool = typer.Option(False, "--force/--no-force", help="Regenerate even if files already exist"),
    output_dir: Optional[Path] = typer.Option(None, "--output-dir", help="Override output directory for visuals"),
):
    """Render visual figures (brain maps, network diagrams) for a condition."""
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    effective_output_dir = output_dir or settings.visuals_dir

    # Determine which slugs to process
    build_all = condition.lower() == "all"

    if build_all:
        try:
            registry = get_registry()
            slugs = registry.list_slugs()
        except Exception:
            slugs = list(VALID_SLUGS)
    else:
        slugs = [condition]

    typer.echo(
        typer.style(
            f"Rendering visuals for {len(slugs)} condition(s)...",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo(f"  Force:      {force}")
    typer.echo(f"  Output dir: {effective_output_dir}")
    typer.echo("")

    VisualsExporter = _import_visuals_exporter()

    total_generated = 0
    failed_slugs: list[str] = []

    try:
        registry = get_registry()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load condition registry: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    for slug in slugs:
        try:
            condition_obj = registry.get(slug)
        except Exception as e:
            typer.echo(typer.style(f"  Condition '{slug}' not found: {e}", fg=typer.colors.RED))
            failed_slugs.append(slug)
            continue

        try:
            exporter = VisualsExporter(Path(effective_output_dir))
            generated = exporter.generate_all(condition_obj, force=force)

            for key, path in generated.items():
                if path is not None:
                    typer.echo(
                        typer.style("  [OK] ", fg=typer.colors.GREEN) + f"{key}: {path}"
                    )
                    total_generated += 1

        except Exception as e:
            typer.echo(
                typer.style(f"  [FAIL] {slug}: {e}", fg=typer.colors.RED)
            )
            failed_slugs.append(slug)

    # Generate shared legends when building all conditions
    if build_all:
        try:
            shared_exporter = VisualsExporter(Path(effective_output_dir))
            shared_paths = shared_exporter.generate_shared_legends()
            for key, path in shared_paths.items():
                if path is not None:
                    typer.echo(
                        typer.style("  [LEGEND] ", fg=typer.colors.CYAN) + f"{key}: {path}"
                    )
                    total_generated += 1
        except Exception as e:
            typer.echo(
                typer.style(f"  Warning: failed to generate shared legends: {e}", fg=typer.colors.YELLOW)
            )

    typer.echo("")
    success_count = len(slugs) - len(failed_slugs)
    typer.echo(
        typer.style(
            f"Generated {total_generated} visual file(s) for {success_count}/{len(slugs)} condition(s).",
            fg=typer.colors.GREEN if not failed_slugs else typer.colors.YELLOW,
        )
    )

    if failed_slugs:
        typer.echo(
            typer.style(
                f"Failed conditions: {', '.join(failed_slugs)}",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit(code=1)
