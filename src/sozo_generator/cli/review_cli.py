"""Manage the clinical review workflow for generated documents."""
from typing import Optional

import typer

try:
    from ..review.manager import ReviewManager
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

review_app = typer.Typer(
    name="review",
    help="Manage the clinical review workflow.",
    add_completion=False,
)


def _get_manager() -> ReviewManager:
    """Create a ReviewManager using the configured reviews directory."""
    try:
        settings = SozoSettings()
    except Exception as e:
        typer.echo(typer.style(f"Failed to load settings: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)
    return ReviewManager(reviews_dir=settings.reviews_dir)


@review_app.command("list")
def list_reviews(
    condition: Optional[str] = typer.Option(None, "--condition", help="Filter by condition slug"),
    all_statuses: bool = typer.Option(False, "--all", help="Show all statuses (default: pending only)"),
):
    """List reviews, showing pending reviews by default."""
    manager = _get_manager()

    try:
        if all_statuses:
            reviews = manager.list_all(condition_slug=condition)
        else:
            reviews = manager.list_pending()
            if condition:
                reviews = [r for r in reviews if r.condition_slug == condition]
    except Exception as e:
        typer.echo(typer.style(f"Failed to list reviews: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    if not reviews:
        label = "reviews" if all_statuses else "pending reviews"
        typer.echo(typer.style(f"No {label} found.", fg=typer.colors.YELLOW))
        return

    # Header
    typer.echo(
        typer.style(
            f"{'Build ID':<45}  {'Condition':<15}  {'Doc Type':<25}  {'Tier':<10}  {'Status':<15}",
            fg=typer.colors.CYAN,
        )
    )
    typer.echo("-" * 115)

    for review in reviews:
        status = review.status.value if hasattr(review.status, "value") else str(review.status)
        # Colour status
        if status == "approved":
            status_styled = typer.style(status, fg=typer.colors.GREEN)
        elif status == "rejected":
            status_styled = typer.style(status, fg=typer.colors.RED)
        elif status == "needs_review":
            status_styled = typer.style(status, fg=typer.colors.YELLOW)
        else:
            status_styled = status

        typer.echo(
            f"  {review.build_id:<43}  {review.condition_slug:<15}  "
            f"{review.document_type:<25}  {review.tier:<10}  {status_styled}"
        )

    typer.echo("")
    typer.echo(
        typer.style(f"Total: {len(reviews)} review(s)", fg=typer.colors.GREEN)
    )


@review_app.command("approve")
def approve_review(
    build_id: str = typer.Option(..., "--build-id", help="Build ID to approve"),
    reviewer: str = typer.Option(..., "--reviewer", help="Reviewer name or identifier"),
    reason: Optional[str] = typer.Option(None, "--reason", help="Approval reason or notes"),
):
    """Approve a build that is pending review."""
    manager = _get_manager()

    try:
        state = manager.approve(
            build_id=build_id,
            reviewer=reviewer,
            reason=reason or "",
        )
    except FileNotFoundError:
        typer.echo(
            typer.style(f"Review not found for build ID: {build_id}", fg=typer.colors.RED)
        )
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(
            typer.style(f"Cannot approve: {e}", fg=typer.colors.RED)
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f"Approval failed: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    typer.echo(
        typer.style(f"Approved: ", fg=typer.colors.GREEN)
        + f"{build_id} by {reviewer}"
    )
    if reason:
        typer.echo(f"  Reason: {reason}")


@review_app.command("reject")
def reject_review(
    build_id: str = typer.Option(..., "--build-id", help="Build ID to reject"),
    reviewer: str = typer.Option(..., "--reviewer", help="Reviewer name or identifier"),
    reason: str = typer.Option(..., "--reason", help="Reason for rejection (required)"),
):
    """Reject a build that is pending review."""
    manager = _get_manager()

    try:
        state = manager.reject(
            build_id=build_id,
            reviewer=reviewer,
            reason=reason,
        )
    except FileNotFoundError:
        typer.echo(
            typer.style(f"Review not found for build ID: {build_id}", fg=typer.colors.RED)
        )
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(
            typer.style(f"Cannot reject: {e}", fg=typer.colors.RED)
        )
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(typer.style(f"Rejection failed: {e}", fg=typer.colors.RED))
        raise typer.Exit(code=1)

    typer.echo(
        typer.style(f"Rejected: ", fg=typer.colors.RED)
        + f"{build_id} by {reviewer}"
    )
    typer.echo(f"  Reason: {reason}")
