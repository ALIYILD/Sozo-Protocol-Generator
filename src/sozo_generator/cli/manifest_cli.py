"""Inspect and list build manifests."""
import json
from pathlib import Path
from typing import Optional

import typer

try:
    from ..orchestration.versioning import ManifestWriter
    from ..core.settings import SozoSettings
except ImportError as e:
    typer.echo(
        typer.style(
            f"Import error: {e}\n"
            "Ensure sozo_generator is installed and all dependencies are available.",
            fg=typer.colors.RED,
        )
    )
    raise SystemExit(1)

manifest_app = typer.Typer(
    name="manifests",
    help="Inspect and list build manifests.",
    add_completion=False,
)


def _get_manifests_dir(manifests_dir: Optional[Path]) -> Path:
    """Resolve the manifests directory from option or settings."""
    if manifests_dir:
        return Path(manifests_dir)
    try:
        settings = SozoSettings()
        return settings.manifests_dir
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)


@manifest_app.command("inspect")
def inspect_manifest(
    build_id: str = typer.Option(..., "--build-id", help="Build ID to inspect"),
    manifests_dir: Optional[Path] = typer.Option(None, "--manifests-dir", help="Override manifests directory"),
):
    """Show detailed information about a build manifest."""
    effective_dir = _get_manifests_dir(manifests_dir)

    try:
        writer = ManifestWriter(manifests_dir=effective_dir)
        manifest = writer.load_manifest(build_id)
    except Exception as e:
        typer.echo(typer.style(f"Failed to load manifest: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    if manifest is None:
        typer.echo(
            typer.style(f"Manifest not found for build ID: {build_id}", fg=typer.colors.RED)
        )
        raise typer.Exit(code=1)

    # Display manifest details
    typer.echo(
        typer.style(f"Build Manifest: {manifest.build_id}", fg=typer.colors.CYAN)
    )
    typer.echo(f"  Condition:    {manifest.condition_name} ({manifest.condition_slug})")
    typer.echo(f"  Built at:     {manifest.built_at}")
    typer.echo(f"  Generator:    {manifest.generator_version}")
    typer.echo(f"  Documents:    {manifest.total_documents}")
    typer.echo(f"  Passed:       {manifest.total_passed}")
    typer.echo(f"  Blocked:      {manifest.total_blocked}")

    if manifest.evidence_snapshot_id:
        typer.echo(f"  Snapshot:     {manifest.evidence_snapshot_id}")
    if manifest.content_hash:
        typer.echo(f"  Content hash: {manifest.content_hash}")

    # Document entries
    if manifest.documents:
        typer.echo("")
        typer.echo(typer.style("  Documents:", fg=typer.colors.CYAN))
        for doc in manifest.documents:
            status_color = typer.colors.GREEN if doc.qa_passed else typer.colors.RED
            status_label = "PASS" if doc.qa_passed else "BLOCK"
            typer.echo(
                typer.style(f"    [{status_label}] ", fg=status_color)
                + f"{doc.tier}/{doc.document_type}"
            )
            if doc.output_path:
                typer.echo(f"           Path: {doc.output_path}")
            if doc.content_hash:
                typer.echo(f"           Hash: {doc.content_hash}")

    # QA summary
    if manifest.qa_summary:
        typer.echo("")
        typer.echo(typer.style("  QA Summary:", fg=typer.colors.CYAN))
        qa = manifest.qa_summary
        typer.echo(f"    Block: {qa.block_count}, Warning: {qa.warning_count}, Info: {qa.info_count}")
        typer.echo(f"    Passed: {qa.passed}")


@manifest_app.command("list")
def list_manifests(
    condition: Optional[str] = typer.Option(None, "--condition", help="Filter by condition slug"),
    manifests_dir: Optional[Path] = typer.Option(None, "--manifests-dir", help="Override manifests directory"),
):
    """List all build manifests."""
    effective_dir = _get_manifests_dir(manifests_dir)

    try:
        writer = ManifestWriter(manifests_dir=effective_dir)
        build_ids = writer.list_manifests(condition_slug=condition)
    except Exception as e:
        typer.echo(typer.style(f"Failed to list manifests: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    if not build_ids:
        label = f"for '{condition}'" if condition else ""
        typer.echo(
            typer.style(f"No manifests found {label}.", fg=typer.colors.YELLOW)
        )
        return

    typer.echo(
        typer.style(
            f"{'Build ID':<50}  {'Details'}",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo("-" * 80)

    for bid in build_ids:
        # Try to load for summary info
        try:
            manifest = writer.load_manifest(bid)
            if manifest:
                passed_color = typer.colors.GREEN if manifest.total_blocked == 0 else typer.colors.YELLOW
                typer.echo(
                    f"  {bid:<48}  "
                    + typer.style(
                        f"{manifest.total_passed}/{manifest.total_documents} passed",
                        fg=passed_color,
                    )
                    + f"  {manifest.condition_name}"
                )
            else:
                typer.echo(f"  {bid}")
        except Exception:
            typer.echo(f"  {bid}")

    typer.echo("")
    typer.echo(
        typer.style(f"Total: {len(build_ids)} manifest(s)", fg=typer.colors.GREEN)
    )
