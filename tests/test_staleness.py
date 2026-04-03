"""Tests for evidence staleness detection."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from sozo_generator.evidence.staleness import (
    EvidenceSnapshot,
    FreshnessLevel,
    StalenessDetector,
    StalenessThresholds,
    SystemStalenessReport,
)


# ── Fixtures ──────────────────────────────────────────────────────────────


@pytest.fixture
def detector(tmp_path):
    """StalenessDetector pointing at tmp directories (no real snapshots)."""
    return StalenessDetector(
        snapshot_dir=str(tmp_path / "evidence_snapshots"),
        staleness_dir=str(tmp_path / "staleness_snapshots"),
    )


@pytest.fixture
def detector_with_snapshot(tmp_path):
    """Detector with a snapshot saved for 'depression'."""
    det = StalenessDetector(
        snapshot_dir=str(tmp_path / "evidence_snapshots"),
        staleness_dir=str(tmp_path / "staleness_snapshots"),
    )
    snapshot = EvidenceSnapshot(
        condition_slug="depression",
        searched_at=datetime.now(timezone.utc) - timedelta(days=10),
        total_articles=45,
        articles_by_level={"high": 10, "medium": 20, "low": 15},
        overall_evidence_level="high",
        top_pmids=["12345678", "23456789"],
        search_queries_used=["depression tDCS"],
        sources_searched=["pubmed"],
    )
    det.save_snapshot(snapshot)
    return det


# ── StalenessDetector with no snapshots ──────────────────────────────────


class TestStalenessDetectorNoSnapshots:
    def test_no_snapshot_returns_never_searched(self, detector):
        report = detector.check_condition("depression", "Depression")
        assert report.freshness == FreshnessLevel.NEVER_SEARCHED
        assert report.last_searched is None
        assert report.days_since_search is None
        assert report.needs_refresh is True
        assert report.refresh_priority == "high"

    def test_never_searched_reason_text(self, detector):
        report = detector.check_condition("unknown_condition")
        assert "No evidence search" in report.reason


# ── Freshness classification thresholds ──────────────────────────────────


class TestFreshnessClassification:
    def test_fresh_within_30_days(self, detector_with_snapshot):
        report = detector_with_snapshot.check_condition("depression", "Depression")
        assert report.freshness == FreshnessLevel.FRESH
        assert report.needs_refresh is False

    def test_aging_after_30_days(self, tmp_path):
        det = StalenessDetector(
            snapshot_dir=str(tmp_path / "ev"),
            staleness_dir=str(tmp_path / "st"),
        )
        snapshot = EvidenceSnapshot(
            condition_slug="anxiety",
            searched_at=datetime.now(timezone.utc) - timedelta(days=60),
            total_articles=20,
            articles_by_level={"medium": 15, "low": 5},
            overall_evidence_level="medium",
            top_pmids=[],
            search_queries_used=["anxiety tavns"],
            sources_searched=["pubmed"],
        )
        det.save_snapshot(snapshot)
        report = det.check_condition("anxiety", "Anxiety")
        assert report.freshness == FreshnessLevel.AGING
        assert report.needs_refresh is False

    def test_stale_after_90_days(self, tmp_path):
        det = StalenessDetector(
            snapshot_dir=str(tmp_path / "ev"),
            staleness_dir=str(tmp_path / "st"),
        )
        snapshot = EvidenceSnapshot(
            condition_slug="ocd",
            searched_at=datetime.now(timezone.utc) - timedelta(days=120),
            total_articles=10,
            articles_by_level={"medium": 10},
            overall_evidence_level="medium",
            top_pmids=[],
            search_queries_used=["ocd tms"],
            sources_searched=["pubmed"],
        )
        det.save_snapshot(snapshot)
        report = det.check_condition("ocd", "OCD")
        assert report.freshness == FreshnessLevel.STALE
        assert report.needs_refresh is True
        assert report.refresh_priority == "medium"

    def test_expired_after_180_days(self, tmp_path):
        det = StalenessDetector(
            snapshot_dir=str(tmp_path / "ev"),
            staleness_dir=str(tmp_path / "st"),
        )
        snapshot = EvidenceSnapshot(
            condition_slug="tinnitus",
            searched_at=datetime.now(timezone.utc) - timedelta(days=200),
            total_articles=5,
            articles_by_level={"low": 5},
            overall_evidence_level="medium",
            top_pmids=[],
            search_queries_used=["tinnitus neurostim"],
            sources_searched=["pubmed"],
        )
        det.save_snapshot(snapshot)
        report = det.check_condition("tinnitus", "Tinnitus")
        assert report.freshness == FreshnessLevel.EXPIRED
        assert report.needs_refresh is True
        assert report.refresh_priority == "high"


# ── SystemStalenessReport.overall_health ──────────────────────────────────


class TestSystemStalenessReportHealth:
    def _make_report(self, **kwargs):
        defaults = dict(
            generated_at=datetime.now(timezone.utc),
            thresholds=StalenessThresholds(),
            conditions=[],
            total_conditions=0,
            fresh_count=0,
            aging_count=0,
            stale_count=0,
            expired_count=0,
            never_searched_count=0,
            high_priority_refreshes=[],
        )
        defaults.update(kwargs)
        return SystemStalenessReport(**defaults)

    def test_healthy_when_all_fresh(self):
        report = self._make_report(total_conditions=5, fresh_count=5)
        assert report.overall_health == "healthy"

    def test_critical_when_expired(self):
        report = self._make_report(total_conditions=5, fresh_count=4, expired_count=1)
        assert report.overall_health == "critical"

    def test_critical_when_never_searched(self):
        report = self._make_report(total_conditions=5, fresh_count=4, never_searched_count=1)
        assert report.overall_health == "critical"

    def test_warning_when_stale(self):
        report = self._make_report(total_conditions=5, fresh_count=4, stale_count=1)
        assert report.overall_health == "warning"

    def test_attention_when_majority_aging(self):
        report = self._make_report(total_conditions=10, fresh_count=3, aging_count=7)
        assert report.overall_health == "attention"


# ── low_evidence_multiplier ──────────────────────────────────────────────


class TestLowEvidenceMultiplier:
    def test_halves_thresholds_for_low_evidence(self, tmp_path):
        det = StalenessDetector(
            snapshot_dir=str(tmp_path / "ev"),
            staleness_dir=str(tmp_path / "st"),
        )
        # 20 days old with low evidence level should be classified as AGING
        # (because 0.5 * 30 = 15 day threshold for "fresh")
        snapshot = EvidenceSnapshot(
            condition_slug="rare_condition",
            searched_at=datetime.now(timezone.utc) - timedelta(days=20),
            total_articles=3,
            articles_by_level={"low": 3},
            overall_evidence_level="low",
            top_pmids=[],
            search_queries_used=["rare condition"],
            sources_searched=["pubmed"],
        )
        det.save_snapshot(snapshot)
        report = det.check_condition("rare_condition", "Rare Condition")
        # With multiplier 0.5: fresh_cutoff=15, aging_cutoff=45
        # 20 days > 15 -> should be AGING
        assert report.freshness == FreshnessLevel.AGING

    def test_default_thresholds_without_multiplier(self, tmp_path):
        det = StalenessDetector(
            snapshot_dir=str(tmp_path / "ev"),
            staleness_dir=str(tmp_path / "st"),
        )
        # 20 days old with high evidence level should still be FRESH (threshold 30)
        snapshot = EvidenceSnapshot(
            condition_slug="common_condition",
            searched_at=datetime.now(timezone.utc) - timedelta(days=20),
            total_articles=50,
            articles_by_level={"high": 30, "medium": 20},
            overall_evidence_level="high",
            top_pmids=[],
            search_queries_used=["common condition"],
            sources_searched=["pubmed"],
        )
        det.save_snapshot(snapshot)
        report = det.check_condition("common_condition", "Common Condition")
        assert report.freshness == FreshnessLevel.FRESH
