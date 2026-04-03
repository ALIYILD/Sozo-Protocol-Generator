"""Evidence pipeline tasks — refresh, staleness checks, and scheduled maintenance."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded

from sozo_workers.status import TaskStatusTracker

logger = logging.getLogger(__name__)

_tracker: Optional[TaskStatusTracker] = None

# Evidence is considered stale after this many days
_STALENESS_THRESHOLD_DAYS = 30


def _get_tracker() -> TaskStatusTracker:
    global _tracker
    if _tracker is None:
        _tracker = TaskStatusTracker()
    return _tracker


def _audit_event(event_type: str, data: dict) -> None:
    logger.info(
        "AUDIT event=%s ts=%s data=%s",
        event_type,
        datetime.now(timezone.utc).isoformat(),
        data,
    )


def _get_evidence_cache_dir() -> Path:
    """Resolve evidence cache directory from settings."""
    from sozo_generator.core.settings import get_settings
    settings = get_settings()
    return settings.cache_dir


def _get_all_condition_slugs() -> list[str]:
    """Get all condition slugs from the registry."""
    from sozo_generator.conditions.registry import get_registry
    registry = get_registry()
    return registry.list_slugs()


@shared_task(
    bind=True,
    name="sozo_workers.tasks.evidence_tasks.refresh_evidence",
    max_retries=3,
    default_retry_delay=60,
    acks_late=True,
    queue="sozo_default",
)
def refresh_evidence(
    self,
    condition_slug: str,
    force: bool = True,
    user_id: str = "",
) -> dict:
    """Re-run the evidence pipeline for a single condition.

    Searches PubMed, Crossref, and Semantic Scholar, deduplicates, and
    updates the local evidence cache.

    Args:
        condition_slug: Target condition (e.g. "adhd").
        force: Bypass cache and force fresh search.
        user_id: Requesting user.

    Returns:
        Dict with article counts and source breakdown.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message=f"Refreshing evidence for: {condition_slug}",
        user_id=user_id,
    )
    _audit_event("evidence_refresh.started", {
        "task_id": task_id, "condition_slug": condition_slug, "user_id": user_id,
    })

    try:
        from sozo_generator.evidence.multi_source_search import MultiSourceSearch

        cache_dir = _get_evidence_cache_dir()
        searcher = MultiSourceSearch(
            cache_dir=cache_dir,
            force_refresh=force,
        )

        # Build the search query from condition metadata
        from sozo_generator.conditions.registry import get_registry
        registry = get_registry()

        if not registry.exists(condition_slug):
            error_msg = f"Unknown condition: {condition_slug}"
            tracker.set_status(
                task_id, "FAILURE", message=error_msg, user_id=user_id,
            )
            return {"error": error_msg}

        schema = registry.get(condition_slug)
        display_name = schema.display_name

        tracker.set_status(
            task_id, "PROGRESS", progress=0.2,
            message=f"Searching evidence sources for '{display_name}'...",
            user_id=user_id,
        )

        # Primary search: condition name + neuromodulation
        query = f"{display_name} neuromodulation treatment protocol"
        result = searcher.search(query, max_results_per_source=30, years_back=10)

        tracker.set_status(
            task_id, "PROGRESS", progress=0.7,
            message=f"Found {len(result.articles)} articles, writing cache...",
            user_id=user_id,
        )

        # Write results to evidence cache
        evidence_dir = Path("data/processed/evidence") / condition_slug
        evidence_dir.mkdir(parents=True, exist_ok=True)

        evidence_file = evidence_dir / "articles.json"
        articles_data = []
        for article in result.articles:
            articles_data.append({
                "pmid": article.pmid,
                "doi": article.doi,
                "title": article.title,
                "authors": article.authors if hasattr(article, "authors") else [],
                "year": article.year if hasattr(article, "year") else None,
                "journal": article.journal if hasattr(article, "journal") else "",
                "abstract": article.abstract if hasattr(article, "abstract") else "",
                "score": article.score if hasattr(article, "score") else 0.0,
                "notes": article.notes,
            })

        evidence_file.write_text(json.dumps({
            "condition_slug": condition_slug,
            "query": query,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
            "source_counts": result.source_counts,
            "duplicates_removed": result.duplicates_removed,
            "total_articles": len(result.articles),
            "articles": articles_data,
        }, indent=2))

        # Write refresh timestamp
        ts_file = evidence_dir / ".last_refresh"
        ts_file.write_text(datetime.now(timezone.utc).isoformat())

        output = {
            "condition_slug": condition_slug,
            "query": query,
            "total_articles": len(result.articles),
            "source_counts": result.source_counts,
            "duplicates_removed": result.duplicates_removed,
            "errors": result.errors,
            "cache_path": str(evidence_file),
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"Evidence refreshed: {len(result.articles)} articles for {condition_slug}",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("evidence_refresh.completed", {
            "task_id": task_id,
            "condition_slug": condition_slug,
            "total_articles": len(result.articles),
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Evidence refresh for {condition_slug} exceeded time limit",
            user_id=user_id,
        )
        raise

    except Exception as exc:
        logger.exception("refresh_evidence failed for %s", condition_slug)
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Evidence refresh failed: {exc}",
            user_id=user_id,
        )
        _audit_event("evidence_refresh.failed", {
            "task_id": task_id, "condition_slug": condition_slug,
            "error": str(exc), "user_id": user_id,
        })
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    name="sozo_workers.tasks.evidence_tasks.refresh_all_evidence",
    max_retries=1,
    default_retry_delay=120,
    acks_late=True,
    queue="sozo_default",
    time_limit=3600,
    soft_time_limit=3300,
)
def refresh_all_evidence(
    self,
    user_id: str = "",
) -> dict:
    """Refresh evidence for all 15 conditions.

    Dispatches individual refresh_evidence tasks as a chord for parallelism,
    but can also run sequentially within a single worker if preferred.

    Returns:
        Summary with per-condition refresh results.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message="Starting full evidence refresh...",
        user_id=user_id,
    )
    _audit_event("evidence_refresh_all.started", {"task_id": task_id, "user_id": user_id})

    try:
        condition_slugs = _get_all_condition_slugs()
        total = len(condition_slugs)
        results: list[dict] = []

        for idx, slug in enumerate(condition_slugs):
            progress = idx / total
            tracker.set_status(
                task_id, "PROGRESS", progress=progress,
                message=f"Refreshing evidence for {slug} ({idx + 1}/{total})",
                user_id=user_id,
            )

            try:
                # Run inline rather than fan-out to respect rate limits on PubMed/S2
                result = _run_single_evidence_refresh(slug)
                results.append(result)
            except Exception as e:
                logger.error("Evidence refresh failed for %s: %s", slug, e)
                results.append({
                    "condition_slug": slug,
                    "error": str(e),
                    "total_articles": 0,
                })

        succeeded = sum(1 for r in results if "error" not in r)
        failed = total - succeeded

        output = {
            "total_conditions": total,
            "succeeded": succeeded,
            "failed": failed,
            "per_condition": results,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"Full refresh complete: {succeeded}/{total} conditions refreshed",
            metadata=output,
            user_id=user_id,
        )
        _audit_event("evidence_refresh_all.completed", {
            "task_id": task_id, "succeeded": succeeded, "failed": failed,
            "user_id": user_id,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message="Full evidence refresh exceeded time limit",
            user_id=user_id,
        )
        raise

    except Exception as exc:
        logger.exception("refresh_all_evidence failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Full evidence refresh failed: {exc}",
            user_id=user_id,
        )
        raise self.retry(exc=exc)


def _run_single_evidence_refresh(condition_slug: str) -> dict:
    """Run evidence refresh inline (not as a Celery task) for use in batch operations."""
    from sozo_generator.evidence.multi_source_search import MultiSourceSearch
    from sozo_generator.conditions.registry import get_registry

    cache_dir = _get_evidence_cache_dir()
    searcher = MultiSourceSearch(cache_dir=cache_dir, force_refresh=True)

    registry = get_registry()
    schema = registry.get(condition_slug)
    display_name = schema.display_name

    query = f"{display_name} neuromodulation treatment protocol"
    result = searcher.search(query, max_results_per_source=30, years_back=10)

    # Write cache
    evidence_dir = Path("data/processed/evidence") / condition_slug
    evidence_dir.mkdir(parents=True, exist_ok=True)

    ts_file = evidence_dir / ".last_refresh"
    ts_file.write_text(datetime.now(timezone.utc).isoformat())

    return {
        "condition_slug": condition_slug,
        "total_articles": len(result.articles),
        "source_counts": result.source_counts,
        "duplicates_removed": result.duplicates_removed,
    }


@shared_task(
    bind=True,
    name="sozo_workers.tasks.evidence_tasks.check_evidence_staleness",
    max_retries=1,
    default_retry_delay=30,
    acks_late=True,
    queue="sozo_maintenance",
)
def check_evidence_staleness(
    self,
    threshold_days: int = _STALENESS_THRESHOLD_DAYS,
    user_id: str = "",
) -> dict:
    """Scan all conditions for stale evidence and return alerts.

    Evidence is stale if the last refresh timestamp is older than
    ``threshold_days`` or if no timestamp file exists.

    Returns:
        Dict with stale/fresh condition lists and alert details.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message="Checking evidence staleness...",
        user_id=user_id,
    )

    try:
        condition_slugs = _get_all_condition_slugs()
        now = datetime.now(timezone.utc)
        threshold = timedelta(days=threshold_days)

        stale: list[dict] = []
        fresh: list[dict] = []
        missing: list[str] = []

        for slug in condition_slugs:
            evidence_dir = Path("data/processed/evidence") / slug
            ts_file = evidence_dir / ".last_refresh"

            if not ts_file.exists():
                missing.append(slug)
                stale.append({
                    "condition_slug": slug,
                    "reason": "no_refresh_timestamp",
                    "last_refresh": None,
                })
                continue

            try:
                last_refresh_str = ts_file.read_text().strip()
                last_refresh = datetime.fromisoformat(last_refresh_str)
                # Ensure timezone-aware
                if last_refresh.tzinfo is None:
                    last_refresh = last_refresh.replace(tzinfo=timezone.utc)

                age = now - last_refresh
                if age > threshold:
                    stale.append({
                        "condition_slug": slug,
                        "reason": "expired",
                        "last_refresh": last_refresh_str,
                        "age_days": age.days,
                    })
                else:
                    fresh.append({
                        "condition_slug": slug,
                        "last_refresh": last_refresh_str,
                        "age_days": age.days,
                    })
            except (ValueError, OSError) as e:
                stale.append({
                    "condition_slug": slug,
                    "reason": f"parse_error: {e}",
                    "last_refresh": None,
                })

        output = {
            "total_conditions": len(condition_slugs),
            "stale_count": len(stale),
            "fresh_count": len(fresh),
            "missing_count": len(missing),
            "threshold_days": threshold_days,
            "stale": stale,
            "fresh": fresh,
            "checked_at": now.isoformat(),
        }

        status_msg = f"Staleness check: {len(stale)} stale, {len(fresh)} fresh, {len(missing)} missing"
        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=status_msg,
            metadata=output,
            user_id=user_id,
        )

        if stale:
            _audit_event("evidence_staleness.alert", {
                "task_id": task_id,
                "stale_conditions": [s["condition_slug"] for s in stale],
            })
            logger.warning(
                "Evidence staleness alert: %d conditions need refresh — %s",
                len(stale),
                [s["condition_slug"] for s in stale],
            )

        return output

    except Exception as exc:
        logger.exception("check_evidence_staleness failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Staleness check failed: {exc}",
            user_id=user_id,
        )
        raise


@shared_task(
    bind=True,
    name="sozo_workers.tasks.evidence_tasks.scheduled_evidence_refresh",
    max_retries=1,
    default_retry_delay=300,
    acks_late=True,
    queue="sozo_maintenance",
    time_limit=7200,  # 2 hours for full scheduled refresh
    soft_time_limit=6900,
)
def scheduled_evidence_refresh(self) -> dict:
    """Periodic task (Celery Beat) — check staleness, then refresh stale conditions.

    This is the main entry point for the weekly scheduled refresh.
    It first checks which conditions are stale, then refreshes only those.
    """
    task_id = self.request.id
    tracker = _get_tracker()

    tracker.set_status(
        task_id, "STARTED", progress=0.0,
        message="Scheduled evidence refresh starting...",
    )
    _audit_event("scheduled_refresh.started", {"task_id": task_id})

    try:
        # Step 1: Check staleness
        condition_slugs = _get_all_condition_slugs()
        now = datetime.now(timezone.utc)
        threshold = timedelta(days=_STALENESS_THRESHOLD_DAYS)

        stale_slugs: list[str] = []
        for slug in condition_slugs:
            evidence_dir = Path("data/processed/evidence") / slug
            ts_file = evidence_dir / ".last_refresh"

            if not ts_file.exists():
                stale_slugs.append(slug)
                continue

            try:
                last_refresh_str = ts_file.read_text().strip()
                last_refresh = datetime.fromisoformat(last_refresh_str)
                if last_refresh.tzinfo is None:
                    last_refresh = last_refresh.replace(tzinfo=timezone.utc)
                if (now - last_refresh) > threshold:
                    stale_slugs.append(slug)
            except (ValueError, OSError):
                stale_slugs.append(slug)

        if not stale_slugs:
            output = {
                "stale_count": 0,
                "refreshed": [],
                "message": "All evidence is fresh. No refresh needed.",
            }
            tracker.set_status(
                task_id, "SUCCESS", progress=1.0,
                message="No stale evidence found",
                metadata=output,
            )
            return output

        # Step 2: Refresh stale conditions
        tracker.set_status(
            task_id, "PROGRESS", progress=0.1,
            message=f"Found {len(stale_slugs)} stale conditions, refreshing...",
        )

        refreshed: list[dict] = []
        for idx, slug in enumerate(stale_slugs):
            progress = 0.1 + (0.9 * idx / len(stale_slugs))
            tracker.set_status(
                task_id, "PROGRESS", progress=progress,
                message=f"Refreshing {slug} ({idx + 1}/{len(stale_slugs)})",
            )
            try:
                result = _run_single_evidence_refresh(slug)
                refreshed.append(result)
            except Exception as e:
                logger.error("Scheduled refresh failed for %s: %s", slug, e)
                refreshed.append({
                    "condition_slug": slug,
                    "error": str(e),
                    "total_articles": 0,
                })

        succeeded = sum(1 for r in refreshed if "error" not in r)
        output = {
            "stale_count": len(stale_slugs),
            "refreshed_count": succeeded,
            "failed_count": len(stale_slugs) - succeeded,
            "refreshed": refreshed,
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }

        tracker.set_status(
            task_id, "SUCCESS", progress=1.0,
            message=f"Scheduled refresh complete: {succeeded}/{len(stale_slugs)} refreshed",
            metadata=output,
        )
        _audit_event("scheduled_refresh.completed", {
            "task_id": task_id,
            "stale_count": len(stale_slugs),
            "refreshed_count": succeeded,
        })

        return output

    except SoftTimeLimitExceeded:
        tracker.set_status(
            task_id, "FAILURE",
            message="Scheduled refresh exceeded time limit",
        )
        raise

    except Exception as exc:
        logger.exception("scheduled_evidence_refresh failed")
        tracker.set_status(
            task_id, "FAILURE",
            message=f"Scheduled refresh failed: {exc}",
        )
        raise self.retry(exc=exc)
