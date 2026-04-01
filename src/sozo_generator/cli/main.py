"""
SOZO Generator CLI — clinical document generation platform.

Usage:
    python -m sozo_generator.cli.main [COMMAND] [OPTIONS]
"""
import typer

# --- Import subcommand apps with graceful error handling ---

try:
    from .build_condition import build_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'build condition' command: {e}", fg=typer.colors.YELLOW))
    build_app = typer.Typer(name="build", help="(unavailable — import error)")

try:
    from .build_all import build_all_app
    _build_all_available = True
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'build all' command: {e}", fg=typer.colors.YELLOW))
    _build_all_available = False

try:
    from .ingest_evidence import evidence_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'ingest-evidence' command: {e}", fg=typer.colors.YELLOW))
    evidence_app = typer.Typer(name="ingest-evidence", help="(unavailable — import error)")

try:
    from .extract_template import extract_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'extract-template' command: {e}", fg=typer.colors.YELLOW))
    extract_app = typer.Typer(name="extract-template", help="(unavailable — import error)")

try:
    from .qa_report import qa_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'qa' command: {e}", fg=typer.colors.YELLOW))
    qa_app = typer.Typer(name="qa", help="(unavailable — import error)")

try:
    from .render_visuals import visuals_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'visuals' command: {e}", fg=typer.colors.YELLOW))
    visuals_app = typer.Typer(name="visuals", help="(unavailable — import error)")

try:
    from .qa_engine_cli import qa_engine_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'qa2' command: {e}", fg=typer.colors.YELLOW))
    qa_engine_app = typer.Typer(name="qa2", help="(unavailable — import error)")

try:
    from .review_cli import review_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'review' command: {e}", fg=typer.colors.YELLOW))
    review_app = typer.Typer(name="review", help="(unavailable — import error)")

try:
    from .evidence_cli import evidence_cli_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'evidence' command: {e}", fg=typer.colors.YELLOW))
    evidence_cli_app = typer.Typer(name="evidence", help="(unavailable — import error)")

try:
    from .manifest_cli import manifest_app
except ImportError as e:
    typer.echo(typer.style(f"Warning: could not load 'manifests' command: {e}", fg=typer.colors.YELLOW))
    manifest_app = typer.Typer(name="manifests", help="(unavailable — import error)")

# ---------------------------------------------------------------------------
# Top-level Typer app
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="sozo-generator",
    help="SOZO Brain Center clinical document generation platform.",
    add_completion=False,
)

# Register subcommand groups
app.add_typer(extract_app, name="extract-template")
app.add_typer(evidence_app, name="ingest-evidence")
app.add_typer(build_app, name="build")
app.add_typer(qa_app, name="qa")
app.add_typer(visuals_app, name="visuals")
app.add_typer(qa_engine_app, name="qa2")
app.add_typer(review_app, name="review")
app.add_typer(evidence_cli_app, name="evidence")
app.add_typer(manifest_app, name="manifests")

# Merge build-all commands into the build group
if _build_all_available:
    from .build_all import build_all_app  # noqa: F811 re-import to be explicit
    # Register the 'all' command from build_all_app directly on build_app
    # so it is accessible as `build all`
    try:
        from .build_all import build_all as _build_all_cmd
        build_app.command("all")(_build_all_cmd)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Top-level commands
# ---------------------------------------------------------------------------

VERSION = "0.1.0"

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]

CONDITION_NAMES = {
    "parkinsons": "Parkinson's Disease",
    "depression": "Major Depressive Disorder",
    "anxiety": "Anxiety Disorders",
    "adhd": "ADHD",
    "alzheimers": "Alzheimer's Disease",
    "post_stroke": "Post-Stroke Rehabilitation",
    "tbi": "Traumatic Brain Injury",
    "chronic_pain": "Chronic Pain",
    "ptsd": "PTSD",
    "ocd": "Obsessive-Compulsive Disorder",
    "ms": "Multiple Sclerosis",
    "autism": "Autism Spectrum Disorder",
    "long_covid": "Long COVID (Post-COVID Syndrome)",
    "tinnitus": "Tinnitus",
    "insomnia": "Insomnia",
}


@app.command("version")
def version():
    """Print the current version of sozo-generator."""
    _version = VERSION
    try:
        # Try to read from pyproject.toml if importlib.metadata is available
        from importlib.metadata import version as pkg_version
        _version = pkg_version("sozo_generator")
    except Exception:
        pass
    typer.echo(f"sozo-generator {_version}")


@app.command("list-conditions")
def list_conditions():
    """List all 15 supported condition slugs with their display names."""
    # Try to pull live data from registry; fall back to built-in list
    try:
        from ..conditions.registry import get_registry  # type: ignore
        registry = get_registry()
        conditions = registry.list_all()
        if conditions:
            typer.echo(
                typer.style(
                    f"{'Slug':<20}  {'Name'}",
                    fg=typer.colors.CYAN,
                )
            )
            typer.echo("-" * 50)
            for c in conditions:
                if isinstance(c, dict):
                    slug = c.get("slug", "?")
                    name = c.get("display_name") or c.get("name", slug)
                else:
                    slug = getattr(c, "slug", "?")
                    name = getattr(c, "display_name", slug)
                typer.echo(f"  {slug:<20}  {name}")
            typer.echo("")
            typer.echo(
                typer.style(f"Total: {len(conditions)} conditions", fg=typer.colors.GREEN)
            )
            return
    except Exception:
        pass

    # Fallback: print built-in list
    typer.echo(
        typer.style(
            f"{'Slug':<20}  {'Name'}",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo("-" * 50)
    for slug in VALID_SLUGS:
        name = CONDITION_NAMES.get(slug, slug)
        typer.echo(f"  {slug:<20}  {name}")
    typer.echo("")
    typer.echo(typer.style(f"Total: {len(VALID_SLUGS)} conditions", fg=typer.colors.GREEN))


if __name__ == "__main__":
    app()
