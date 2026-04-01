"""Evidence snapshot management CLI."""
from typing import Optional

import typer

try:
    from ..evidence.snapshots import SnapshotManager
    from ..evidence.bundles import BundleStore
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

evidence_cli_app = typer.Typer(
    name="evidence",
    help="Manage evidence snapshots.",
    add_completion=False,
)

VALID_SLUGS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "post_stroke", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "autism", "long_covid", "tinnitus", "insomnia",
]


@evidence_cli_app.command("freeze")
def freeze_evidence(
    condition: str = typer.Option(..., "--condition", help="Condition slug (e.g. parkinsons)"),
):
    """Create an immutable evidence snapshot for a condition.

    Loads all existing evidence bundles for the condition and freezes them
    into a versioned snapshot with a content hash.
    """
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    # Validate condition slug
    try:
        registry = get_registry()
        condition_obj = registry.get(condition)
    except Exception as e:
        typer.echo(typer.style(f"Condition '{condition}' not found: {e}", fg=typer.colors.RED))
        typer.echo(
            typer.style(f"Valid slugs: {', '.join(VALID_SLUGS)}", fg=typer.colors.YELLOW)
        )
        raise typer.Exit(code=1)

    condition_name = (
        condition_obj.get("display_name", condition)
        if isinstance(condition_obj, dict)
        else getattr(condition_obj, "display_name", condition)
    )

    typer.echo(
        typer.style(f"Freezing evidence for: {condition_name}", fg=typer.colors.CYAN)
    )

    # Load bundles from store
    try:
        bundle_store = BundleStore(store_dir=settings.evidence_dir)
        bundles = bundle_store.get_all(condition)
    except Exception as e:
        typer.echo(typer.style(f"Failed to load bundles: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    if not bundles:
        typer.echo(
            typer.style(
                f"No evidence bundles found for '{condition}'. "
                "Run 'ingest-evidence ingest' first.",
                fg=typer.colors.YELLOW,
            )
        )
        raise typer.Exit(code=1)

    typer.echo(f"  Bundles found: {len(bundles)}")
    total_items = sum(len(b.items) for b in bundles)
    typer.echo(f"  Total articles: {total_items}")

    # Collect search queries from bundles
    search_queries = []
    for b in bundles:
        if hasattr(b, "search_query") and b.search_query:
            search_queries.append(b.search_query)

    # Create snapshot
    try:
        snapshot_mgr = SnapshotManager(snapshots_dir=settings.snapshots_dir)
        manifest = snapshot_mgr.create_snapshot(
            condition_slug=condition,
            bundles=bundles,
            search_queries=search_queries,
            notes=f"CLI freeze for {condition_name}",
        )
    except Exception as e:
        typer.echo(typer.style(f"Snapshot creation failed: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    typer.echo("")
    typer.echo(typer.style("  [OK] ", fg=typer.colors.GREEN) + f"Snapshot ID: {manifest.snapshot_id}")
    typer.echo(f"  Content hash: {manifest.content_hash}")
    typer.echo(f"  Articles: {manifest.total_articles}")
    typer.echo(f"  Bundles: {len(bundles)}")
    typer.echo("")
    typer.echo(
        typer.style(
            f"Evidence snapshot created for '{condition}'.",
            fg=typer.colors.GREEN,
        )
    )
