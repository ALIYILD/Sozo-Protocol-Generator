"""Evidence staleness detection and freshness management.

Monitors the age and quality of evidence backing each protocol and condition.
Alerts when evidence needs refreshing based on configurable thresholds.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Optional

import json
import logging

logger = logging.getLogger(__name__)


class FreshnessLevel(str, Enum):
    """Evidence freshness classification."""
    FRESH = "fresh"           # < 30 days since last search
    AGING = "aging"           # 30-90 days
    STALE = "stale"           # 90-180 days
    EXPIRED = "expired"       # > 180 days
    NEVER_SEARCHED = "never"  # No evidence search recorded


@dataclass
class StalenessThresholds:
    """Configurable thresholds for staleness classification."""
    fresh_days: int = 30
    aging_days: int = 90
    stale_days: int = 180
    # Conditions with lower evidence quality get more aggressive refresh
    low_evidence_multiplier: float = 0.5  # halve thresholds for LOW/VERY_LOW


@dataclass
class EvidenceSnapshot:
    """Point-in-time record of evidence state for a condition."""
    condition_slug: str
    searched_at: datetime
    total_articles: int
    articles_by_level: dict[str, int]
    overall_evidence_level: str
    top_pmids: list[str]  # top 10 by relevance
    search_queries_used: list[str]
    sources_searched: list[str]  # pubmed, crossref, semantic_scholar


@dataclass
class StalenessReport:
    """Staleness assessment for a single condition."""
    condition_slug: str
    condition_name: str
    freshness: FreshnessLevel
    last_searched: Optional[datetime]
    days_since_search: Optional[int]
    total_articles: int
    evidence_level: str
    needs_refresh: bool
    refresh_priority: str  # high, medium, low
    reason: str
    new_articles_estimated: Optional[int] = None  # from PubMed date-filtered count


@dataclass
class SystemStalenessReport:
    """Full staleness report across all conditions."""
    generated_at: datetime
    thresholds: StalenessThresholds
    conditions: list[StalenessReport]
    total_conditions: int
    fresh_count: int
    aging_count: int
    stale_count: int
    expired_count: int
    never_searched_count: int
    high_priority_refreshes: list[str]  # condition slugs needing urgent refresh

    @property
    def overall_health(self) -> str:
        if self.expired_count > 0 or self.never_searched_count > 0:
            return "critical"
        if self.stale_count > 0:
            return "warning"
        if self.aging_count > self.total_conditions * 0.5:
            return "attention"
        return "healthy"

    def to_dict(self) -> dict:
        """Serialize the full report to a JSON-safe dict."""
        return {
            "generated_at": self.generated_at.isoformat(),
            "overall_health": self.overall_health,
            "thresholds": {
                "fresh_days": self.thresholds.fresh_days,
                "aging_days": self.thresholds.aging_days,
                "stale_days": self.thresholds.stale_days,
                "low_evidence_multiplier": self.thresholds.low_evidence_multiplier,
            },
            "summary": {
                "total_conditions": self.total_conditions,
                "fresh": self.fresh_count,
                "aging": self.aging_count,
                "stale": self.stale_count,
                "expired": self.expired_count,
                "never_searched": self.never_searched_count,
            },
            "high_priority_refreshes": self.high_priority_refreshes,
            "conditions": [
                {
                    "slug": r.condition_slug,
                    "name": r.condition_name,
                    "freshness": r.freshness.value,
                    "last_searched": r.last_searched.isoformat() if r.last_searched else None,
                    "days_since_search": r.days_since_search,
                    "total_articles": r.total_articles,
                    "evidence_level": r.evidence_level,
                    "needs_refresh": r.needs_refresh,
                    "refresh_priority": r.refresh_priority,
                    "reason": r.reason,
                    "new_articles_estimated": r.new_articles_estimated,
                }
                for r in self.conditions
            ],
        }


class StalenessDetector:
    """Detects and reports evidence staleness across all conditions.

    Uses the existing SnapshotManager for reading manifest-based snapshots,
    and maintains its own lightweight staleness snapshot files for fast lookups.
    """

    SNAPSHOT_DIR = "data/evidence_snapshots"
    STALENESS_DIR = "data/staleness_snapshots"

    def __init__(
        self,
        thresholds: Optional[StalenessThresholds] = None,
        snapshot_dir: Optional[str] = None,
        staleness_dir: Optional[str] = None,
    ):
        self.thresholds = thresholds or StalenessThresholds()
        self.snapshot_dir = Path(snapshot_dir or self.SNAPSHOT_DIR)
        self.staleness_dir = Path(staleness_dir or self.STALENESS_DIR)

    def check_condition(self, condition_slug: str, condition_name: str = "") -> StalenessReport:
        """Check staleness for a single condition."""
        snapshot = self._load_latest_snapshot(condition_slug)

        if snapshot is None:
            logger.info(
                "No evidence snapshot found for condition '%s' — marking as NEVER_SEARCHED",
                condition_slug,
            )
            return StalenessReport(
                condition_slug=condition_slug,
                condition_name=condition_name,
                freshness=FreshnessLevel.NEVER_SEARCHED,
                last_searched=None,
                days_since_search=None,
                total_articles=0,
                evidence_level="missing",
                needs_refresh=True,
                refresh_priority="high",
                reason="No evidence search has been performed for this condition.",
            )

        now = datetime.now(timezone.utc)
        searched_at = snapshot.searched_at
        # Ensure both datetimes are tz-aware for safe subtraction
        if searched_at.tzinfo is None:
            searched_at = searched_at.replace(tzinfo=timezone.utc)
        days_since = (now - searched_at).days

        # Adjust thresholds for low-evidence conditions
        multiplier = 1.0
        if snapshot.overall_evidence_level in ("low", "very_low"):
            multiplier = self.thresholds.low_evidence_multiplier
            logger.debug(
                "Applying low-evidence multiplier (%.1f) for '%s' (level=%s)",
                multiplier, condition_slug, snapshot.overall_evidence_level,
            )

        fresh_cutoff = int(self.thresholds.fresh_days * multiplier)
        aging_cutoff = int(self.thresholds.aging_days * multiplier)
        stale_cutoff = int(self.thresholds.stale_days * multiplier)

        if days_since <= fresh_cutoff:
            freshness = FreshnessLevel.FRESH
        elif days_since <= aging_cutoff:
            freshness = FreshnessLevel.AGING
        elif days_since <= stale_cutoff:
            freshness = FreshnessLevel.STALE
        else:
            freshness = FreshnessLevel.EXPIRED

        needs_refresh = freshness in (FreshnessLevel.STALE, FreshnessLevel.EXPIRED)

        if freshness == FreshnessLevel.EXPIRED:
            priority = "high"
            reason = f"Evidence is {days_since} days old (>{stale_cutoff} day threshold)."
        elif freshness == FreshnessLevel.STALE:
            priority = "medium"
            reason = f"Evidence is {days_since} days old (>{aging_cutoff} day threshold)."
        elif freshness == FreshnessLevel.AGING:
            priority = "low"
            reason = f"Evidence is {days_since} days old, approaching staleness threshold."
            needs_refresh = False  # Not yet, but flagged
        else:
            priority = "low"
            reason = "Evidence is current."

        logger.info(
            "Staleness check for '%s': %s (days=%d, articles=%d, level=%s, priority=%s)",
            condition_slug, freshness.value, days_since,
            snapshot.total_articles, snapshot.overall_evidence_level, priority,
        )

        return StalenessReport(
            condition_slug=condition_slug,
            condition_name=condition_name,
            freshness=freshness,
            last_searched=snapshot.searched_at,
            days_since_search=days_since,
            total_articles=snapshot.total_articles,
            evidence_level=snapshot.overall_evidence_level,
            needs_refresh=needs_refresh,
            refresh_priority=priority,
            reason=reason,
        )

    def check_all_conditions(self, conditions: dict[str, str]) -> SystemStalenessReport:
        """Check staleness for all conditions.

        Args:
            conditions: {slug: display_name} mapping
        """
        logger.info("Running staleness check for %d conditions", len(conditions))
        reports = [self.check_condition(slug, name) for slug, name in conditions.items()]

        fresh = sum(1 for r in reports if r.freshness == FreshnessLevel.FRESH)
        aging = sum(1 for r in reports if r.freshness == FreshnessLevel.AGING)
        stale = sum(1 for r in reports if r.freshness == FreshnessLevel.STALE)
        expired = sum(1 for r in reports if r.freshness == FreshnessLevel.EXPIRED)
        never = sum(1 for r in reports if r.freshness == FreshnessLevel.NEVER_SEARCHED)

        high_priority = [r.condition_slug for r in reports if r.refresh_priority == "high"]

        report = SystemStalenessReport(
            generated_at=datetime.now(timezone.utc),
            thresholds=self.thresholds,
            conditions=reports,
            total_conditions=len(reports),
            fresh_count=fresh,
            aging_count=aging,
            stale_count=stale,
            expired_count=expired,
            never_searched_count=never,
            high_priority_refreshes=high_priority,
        )

        logger.info(
            "Staleness report: health=%s | fresh=%d aging=%d stale=%d expired=%d never=%d | high_priority=%s",
            report.overall_health, fresh, aging, stale, expired, never,
            high_priority or "(none)",
        )

        return report

    def save_snapshot(self, snapshot: EvidenceSnapshot) -> Path:
        """Save an evidence snapshot after a search run.

        Snapshots are stored as JSON at:
            staleness_dir/{condition_slug}/stale-{condition_slug}-{YYYYMMDDHHMMSS}.json

        Returns:
            Path to the written snapshot file.
        """
        condition_dir = self.staleness_dir / snapshot.condition_slug
        condition_dir.mkdir(parents=True, exist_ok=True)

        searched_at = snapshot.searched_at
        if searched_at.tzinfo is None:
            searched_at = searched_at.replace(tzinfo=timezone.utc)
        timestamp = searched_at.strftime("%Y%m%d%H%M%S")
        filename = f"stale-{snapshot.condition_slug}-{timestamp}.json"
        file_path = condition_dir / filename

        data = {
            "condition_slug": snapshot.condition_slug,
            "searched_at": searched_at.isoformat(),
            "total_articles": snapshot.total_articles,
            "articles_by_level": snapshot.articles_by_level,
            "overall_evidence_level": snapshot.overall_evidence_level,
            "top_pmids": snapshot.top_pmids,
            "search_queries_used": snapshot.search_queries_used,
            "sources_searched": snapshot.sources_searched,
        }

        try:
            file_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            logger.info(
                "Saved staleness snapshot for '%s': %s (%d articles)",
                snapshot.condition_slug, file_path.name, snapshot.total_articles,
            )
        except OSError as exc:
            logger.error(
                "Failed to save staleness snapshot for '%s': %s",
                snapshot.condition_slug, exc,
            )
            raise

        return file_path

    def _load_latest_snapshot(self, condition_slug: str) -> Optional[EvidenceSnapshot]:
        """Load the most recent snapshot for a condition.

        Checks two sources in order:
        1. Staleness-specific snapshots in self.staleness_dir (lightweight, written by save_snapshot)
        2. Full evidence snapshots from SnapshotManager in self.snapshot_dir (written by the PRISMA pipeline)

        Returns the newest across both sources, or None.
        """
        candidates: list[EvidenceSnapshot] = []

        # Source 1: staleness snapshots
        staleness_snap = self._load_latest_staleness_snapshot(condition_slug)
        if staleness_snap is not None:
            candidates.append(staleness_snap)

        # Source 2: full evidence manifest snapshots (via SnapshotManager file layout)
        manifest_snap = self._load_latest_manifest_snapshot(condition_slug)
        if manifest_snap is not None:
            candidates.append(manifest_snap)

        if not candidates:
            return None

        # Return the most recent
        def _ensure_tz(dt: datetime) -> datetime:
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

        candidates.sort(key=lambda s: _ensure_tz(s.searched_at), reverse=True)
        return candidates[0]

    def _load_latest_staleness_snapshot(self, condition_slug: str) -> Optional[EvidenceSnapshot]:
        """Load latest staleness-format snapshot from staleness_dir."""
        condition_dir = self.staleness_dir / condition_slug
        if not condition_dir.exists():
            return None

        snapshot_files = sorted(condition_dir.glob(f"stale-{condition_slug}-*.json"))
        if not snapshot_files:
            return None

        # Last file is newest (filenames contain timestamp, lexicographic sort works)
        latest_path = snapshot_files[-1]
        return self._parse_staleness_file(latest_path)

    def _parse_staleness_file(self, path: Path) -> Optional[EvidenceSnapshot]:
        """Parse a staleness snapshot JSON file into an EvidenceSnapshot."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            searched_at = datetime.fromisoformat(data["searched_at"])
            return EvidenceSnapshot(
                condition_slug=data["condition_slug"],
                searched_at=searched_at,
                total_articles=data.get("total_articles", 0),
                articles_by_level=data.get("articles_by_level", {}),
                overall_evidence_level=data.get("overall_evidence_level", "missing"),
                top_pmids=data.get("top_pmids", []),
                search_queries_used=data.get("search_queries_used", []),
                sources_searched=data.get("sources_searched", []),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.warning("Failed to parse staleness snapshot '%s': %s", path, exc)
            return None

    def _load_latest_manifest_snapshot(self, condition_slug: str) -> Optional[EvidenceSnapshot]:
        """Load latest full-pipeline manifest snapshot and convert to EvidenceSnapshot.

        Reads the SnapshotManager file layout:
            snapshot_dir/{condition_slug}/snap-{condition_slug}-{timestamp}.json
        """
        condition_dir = self.snapshot_dir / condition_slug
        if not condition_dir.exists():
            return None

        snapshot_files = sorted(condition_dir.glob(f"snap-{condition_slug}-*.json"))
        if not snapshot_files:
            return None

        latest_path = snapshot_files[-1]
        try:
            data = json.loads(latest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to read manifest snapshot '%s': %s", latest_path, exc)
            return None

        # Extract searched_at from created_at or pubmed_fetch_date
        searched_at = self._parse_manifest_date(data)

        # Tally articles by evidence level from bundles
        articles_by_level: dict[str, int] = {}
        top_pmids: list[str] = []
        search_queries = data.get("search_queries", [])
        bundles = data.get("bundles", [])

        for bundle in bundles:
            for item in bundle.get("items", []):
                level = item.get("evidence_level", "missing")
                articles_by_level[level] = articles_by_level.get(level, 0) + 1
                pmid = item.get("pmid")
                if pmid and pmid not in top_pmids:
                    top_pmids.append(pmid)

        total_articles = data.get("total_articles", sum(articles_by_level.values()))

        # Determine overall evidence level from the distribution
        overall_level = self._compute_overall_level(articles_by_level)

        return EvidenceSnapshot(
            condition_slug=condition_slug,
            searched_at=searched_at,
            total_articles=total_articles,
            articles_by_level=articles_by_level,
            overall_evidence_level=overall_level,
            top_pmids=top_pmids[:10],
            search_queries_used=search_queries,
            sources_searched=["pubmed"],  # manifest snapshots are PubMed-sourced
        )

    def _parse_manifest_date(self, data: dict) -> datetime:
        """Extract the best available date from a manifest snapshot."""
        # Try created_at first (ISO format from contracts.py)
        created_at = data.get("created_at")
        if created_at:
            try:
                return datetime.fromisoformat(created_at)
            except ValueError:
                pass

        # Try pubmed_fetch_date (YYYY-MM-DD)
        fetch_date = data.get("pubmed_fetch_date")
        if fetch_date:
            try:
                return datetime.strptime(fetch_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        # Try to extract timestamp from snapshot_id: snap-{slug}-{YYYYMMDDHHMMSS}
        snapshot_id = data.get("snapshot_id", "")
        parts = snapshot_id.rsplit("-", 1)
        if len(parts) == 2 and len(parts[1]) == 14:
            try:
                return datetime.strptime(parts[1], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            except ValueError:
                pass

        logger.warning(
            "Could not determine date for manifest snapshot '%s', using epoch",
            data.get("snapshot_id", "unknown"),
        )
        return datetime(2000, 1, 1, tzinfo=timezone.utc)

    @staticmethod
    def _compute_overall_level(articles_by_level: dict[str, int]) -> str:
        """Compute overall evidence level from article counts per level.

        Uses the highest level that has at least 2 articles, or falls back
        to the single highest article if no level has 2+.
        """
        if not articles_by_level:
            return "missing"

        level_rank = {
            "highest": 5,
            "high": 4,
            "medium": 3,
            "low": 2,
            "very_low": 1,
            "missing": 0,
        }

        # Prefer levels with 2+ articles (robust evidence)
        robust = {
            lvl: count for lvl, count in articles_by_level.items() if count >= 2
        }
        pool = robust if robust else articles_by_level

        best_level = max(pool.keys(), key=lambda lvl: level_rank.get(lvl, 0))
        return best_level

    def _load_all_snapshots(self, condition_slug: str) -> list[EvidenceSnapshot]:
        """Load all snapshots for trend analysis, sorted chronologically.

        Merges both staleness snapshots and manifest snapshots.
        """
        snapshots: list[EvidenceSnapshot] = []

        # Staleness snapshots
        staleness_dir = self.staleness_dir / condition_slug
        if staleness_dir.exists():
            for path in sorted(staleness_dir.glob(f"stale-{condition_slug}-*.json")):
                snap = self._parse_staleness_file(path)
                if snap is not None:
                    snapshots.append(snap)

        # Manifest snapshots
        manifest_dir = self.snapshot_dir / condition_slug
        if manifest_dir.exists():
            for path in sorted(manifest_dir.glob(f"snap-{condition_slug}-*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError) as exc:
                    logger.warning("Skipping unreadable manifest '%s': %s", path, exc)
                    continue

                searched_at = self._parse_manifest_date(data)
                articles_by_level: dict[str, int] = {}
                top_pmids: list[str] = []
                for bundle in data.get("bundles", []):
                    for item in bundle.get("items", []):
                        level = item.get("evidence_level", "missing")
                        articles_by_level[level] = articles_by_level.get(level, 0) + 1
                        pmid = item.get("pmid")
                        if pmid and pmid not in top_pmids:
                            top_pmids.append(pmid)

                snapshots.append(EvidenceSnapshot(
                    condition_slug=condition_slug,
                    searched_at=searched_at,
                    total_articles=data.get("total_articles", sum(articles_by_level.values())),
                    articles_by_level=articles_by_level,
                    overall_evidence_level=self._compute_overall_level(articles_by_level),
                    top_pmids=top_pmids[:10],
                    search_queries_used=data.get("search_queries", []),
                    sources_searched=["pubmed"],
                ))

        # Deduplicate by timestamp (prefer staleness snapshots if same second)
        seen_timestamps: set[str] = set()
        deduped: list[EvidenceSnapshot] = []
        for snap in snapshots:
            ts_key = f"{snap.condition_slug}-{snap.searched_at.isoformat()}"
            if ts_key not in seen_timestamps:
                seen_timestamps.add(ts_key)
                deduped.append(snap)

        def _ensure_tz(dt: datetime) -> datetime:
            return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)

        deduped.sort(key=lambda s: _ensure_tz(s.searched_at))

        logger.debug(
            "Loaded %d snapshots for '%s' (staleness + manifest)",
            len(deduped), condition_slug,
        )
        return deduped


# --- Convenience functions ---

def get_staleness_report(conditions: Optional[dict[str, str]] = None) -> SystemStalenessReport:
    """Get full staleness report. Uses condition registry if conditions not provided."""
    if conditions is None:
        # Try to load from condition registry
        conditions = _load_condition_registry()
    detector = StalenessDetector()
    return detector.check_all_conditions(conditions)


def _load_condition_registry() -> dict[str, str]:
    """Load condition slugs and names from the registry."""
    # The 15 known conditions
    return {
        "parkinsons": "Parkinson's Disease",
        "depression": "Major Depressive Disorder",
        "anxiety": "Generalized Anxiety Disorder",
        "adhd": "ADHD",
        "alzheimers": "Alzheimer's / MCI",
        "stroke_rehab": "Post-Stroke Rehabilitation",
        "tbi": "Traumatic Brain Injury",
        "chronic_pain": "Chronic Pain / Fibromyalgia",
        "ptsd": "PTSD",
        "ocd": "OCD",
        "ms": "Multiple Sclerosis",
        "asd": "Autism Spectrum Disorder",
        "long_covid": "Long COVID",
        "tinnitus": "Tinnitus",
        "insomnia": "Insomnia",
    }
