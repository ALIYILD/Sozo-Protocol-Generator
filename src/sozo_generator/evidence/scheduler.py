"""
Evidence Auto-Refresh Scheduler.

Periodically refreshes PubMed evidence for all conditions. Can be run as:
1. CLI command: `sozo evidence-refresh --all`
2. Scheduled job (e.g., weekly cron)
3. Programmatically from GenerationService

The scheduler:
- Iterates over all 15 conditions
- Loads each condition's evidence profile from data/reference/evidence_profiles/
- Runs PubMed searches for each claim category
- Updates the local evidence cache
- Logs what was refreshed and any new findings

IMPORTANT: Never fabricates evidence. Only caches real PubMed results.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RefreshResult:
    """Result of refreshing evidence for one condition."""

    condition_slug: str
    articles_fetched: int = 0
    articles_new: int = 0
    articles_cached: int = 0
    errors: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    success: bool = True


@dataclass
class BatchRefreshReport:
    """Summary of a full evidence refresh run."""

    started_at: str = ""
    completed_at: str = ""
    conditions_refreshed: int = 0
    total_articles: int = 0
    total_new: int = 0
    results: list[RefreshResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class EvidenceRefreshScheduler:
    """Manages scheduled evidence refresh for all conditions.

    Usage:
        scheduler = EvidenceRefreshScheduler()

        # Refresh one condition
        result = scheduler.refresh_condition("parkinsons")

        # Refresh all conditions
        report = scheduler.refresh_all()

        # Refresh with custom settings
        report = scheduler.refresh_all(max_results_per_query=50, force=True)
    """

    def __init__(
        self,
        cache_dir: str | Path | None = None,
        profiles_dir: str | Path | None = None,
        max_results_per_query: int = 30,
    ):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("data/raw/pubmed_cache")
        self.profiles_dir = Path(profiles_dir) if profiles_dir else Path("data/reference/evidence_profiles")
        self.max_results = max_results_per_query
        self._client = None

    @property
    def pubmed_client(self):
        if self._client is None:
            try:
                from .pubmed_client import PubMedClient
                self._client = PubMedClient(
                    cache_dir=self.cache_dir,
                    force_refresh=False,
                )
            except Exception as e:
                logger.warning(f"PubMed client unavailable: {e}")
        return self._client

    def refresh_condition(
        self,
        condition_slug: str,
        force: bool = False,
        max_results: int | None = None,
    ) -> RefreshResult:
        """Refresh evidence for a single condition.

        Args:
            condition_slug: Condition to refresh
            force: If True, bypass cache and re-fetch
            max_results: Override max results per query

        Returns:
            RefreshResult with counts and errors
        """
        start = time.time()
        result = RefreshResult(condition_slug=condition_slug)
        max_r = max_results or self.max_results

        if self.pubmed_client is None:
            result.errors.append("PubMed client not available (Biopython not installed)")
            result.success = False
            return result

        # Force refresh if requested
        if force:
            self.pubmed_client.force_refresh = True

        # Load evidence profile
        profile = self._load_profile(condition_slug)
        if not profile:
            result.errors.append(f"No evidence profile found for {condition_slug}")
            result.success = False
            return result

        # Run searches
        search_profiles = profile.get("search_profiles", {})
        for category, search_config in search_profiles.items():
            query = search_config.get("query", "")
            if not query:
                continue

            try:
                articles = self.pubmed_client.search(
                    query=query,
                    max_results=max_r,
                )
                result.articles_fetched += len(articles)
                logger.info(
                    f"  {condition_slug}/{category}: {len(articles)} articles"
                )
            except Exception as e:
                result.errors.append(f"{category}: {e}")
                logger.warning(f"Search failed for {condition_slug}/{category}: {e}")

        # Reset force_refresh
        self.pubmed_client.force_refresh = False

        result.duration_seconds = time.time() - start
        result.success = len(result.errors) == 0
        return result

    def refresh_all(
        self,
        conditions: list[str] | None = None,
        force: bool = False,
        max_results: int | None = None,
        delay_between: float = 1.0,
    ) -> BatchRefreshReport:
        """Refresh evidence for all (or specified) conditions.

        Args:
            conditions: List of slugs, or None for all
            force: Bypass cache
            max_results: Override max per query
            delay_between: Seconds to wait between conditions (rate limiting)

        Returns:
            BatchRefreshReport
        """
        report = BatchRefreshReport(
            started_at=datetime.utcnow().isoformat() + "Z",
        )

        if conditions is None:
            conditions = self._list_available_profiles()

        logger.info(f"Evidence refresh starting for {len(conditions)} conditions")

        for slug in conditions:
            logger.info(f"Refreshing: {slug}")
            result = self.refresh_condition(slug, force=force, max_results=max_results)
            report.results.append(result)
            report.total_articles += result.articles_fetched

            if result.errors:
                report.errors.extend(f"{slug}: {e}" for e in result.errors)

            if delay_between > 0:
                time.sleep(delay_between)

        report.conditions_refreshed = sum(1 for r in report.results if r.success)
        report.completed_at = datetime.utcnow().isoformat() + "Z"

        logger.info(
            f"Evidence refresh complete: {report.conditions_refreshed}/{len(conditions)} "
            f"conditions, {report.total_articles} articles fetched"
        )
        return report

    def _load_profile(self, condition_slug: str) -> Optional[dict]:
        """Load evidence profile YAML for a condition."""
        import yaml
        profile_path = self.profiles_dir / f"{condition_slug}.yaml"
        if not profile_path.exists():
            return None
        try:
            with open(profile_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.warning(f"Failed to load profile {profile_path}: {e}")
            return None

    def _list_available_profiles(self) -> list[str]:
        """List all conditions that have evidence profiles."""
        if not self.profiles_dir.exists():
            return []
        return sorted(
            p.stem for p in self.profiles_dir.glob("*.yaml")
            if not p.stem.startswith("_")
        )

    def get_refresh_status(self) -> dict:
        """Get current refresh status — which conditions have cached evidence."""
        status = {}
        if self.cache_dir.exists():
            cache_files = list(self.cache_dir.glob("*.json"))
            status["cache_files"] = len(cache_files)
            if cache_files:
                newest = max(f.stat().st_mtime for f in cache_files)
                from datetime import datetime
                status["newest_cache"] = datetime.fromtimestamp(newest).isoformat()
        status["available_profiles"] = self._list_available_profiles()
        return status
