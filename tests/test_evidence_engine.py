"""Tests for the evidence engine modules — query planner, deduper, ranker,
clusterer, contradiction detector, snapshot manager, and bundle store."""
from __future__ import annotations

import pytest

from sozo_generator.core.enums import (
    ClaimCategory,
    ConfidenceLabel,
    EvidenceLevel,
    EvidenceRelation,
    EvidenceType,
    Modality,
    NetworkKey,
)
from sozo_generator.schemas.contracts import EvidenceBundle, EvidenceItem

# ── Helpers ─────────────────────────────────────────────────────────────


def _make_item(
    pmid: str = "12345678",
    title: str = "A study",
    relevance: float = 5.0,
    level: EvidenceLevel = EvidenceLevel.MEDIUM,
    relation: EvidenceRelation = EvidenceRelation.SUPPORTS,
    year: int | None = 2024,
    key_finding: str = "",
    modalities: list[Modality] | None = None,
) -> EvidenceItem:
    return EvidenceItem(
        pmid=pmid,
        title=title,
        relevance_score=relevance,
        evidence_level=level,
        relation=relation,
        year=year,
        key_finding=key_finding,
        modalities=modalities or [],
    )


def _make_bundle(
    bundle_id: str = "b1",
    condition_slug: str = "test",
    category: ClaimCategory = ClaimCategory.PATHOPHYSIOLOGY,
    items: list[EvidenceItem] | None = None,
) -> EvidenceBundle:
    return EvidenceBundle(
        bundle_id=bundle_id,
        condition_slug=condition_slug,
        category=category,
        items=items or [],
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# QueryPlanner
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestQueryPlanner:
    def test_plan_condition_returns_query_plan(self):
        from sozo_generator.evidence.query_planner import QueryPlanner

        planner = QueryPlanner()
        plan = planner.plan_condition(
            condition_slug="parkinsons",
            display_name="Parkinson's Disease",
            icd10="G20",
            networks=[NetworkKey.SMN, NetworkKey.DMN],
            modalities=[Modality.TDCS, Modality.TPS],
            symptoms=["tremor", "bradykinesia"],
        )
        assert plan.condition_slug == "parkinsons"
        assert len(plan.queries) > 0

    def test_plan_covers_multiple_categories(self):
        from sozo_generator.evidence.query_planner import QueryPlanner

        planner = QueryPlanner()
        plan = planner.plan_condition(
            condition_slug="depression",
            display_name="Major Depressive Disorder",
            modalities=[Modality.TDCS],
        )
        coverage = plan.category_coverage
        # Should cover at least pathophysiology, brain regions, stimulation, safety
        assert ClaimCategory.PATHOPHYSIOLOGY in coverage
        assert ClaimCategory.BRAIN_REGIONS in coverage
        assert ClaimCategory.SAFETY in coverage
        assert ClaimCategory.STIMULATION_TARGETS in coverage
        assert len(coverage) >= 8

    def test_plan_total_max_results(self):
        from sozo_generator.evidence.query_planner import QueryPlanner

        planner = QueryPlanner()
        plan = planner.plan_condition(
            condition_slug="test",
            display_name="Test Condition",
        )
        assert plan.total_max_results > 0
        assert plan.total_max_results == sum(q.max_results for q in plan.queries)

    def test_plan_with_no_networks_or_symptoms(self):
        from sozo_generator.evidence.query_planner import QueryPlanner

        planner = QueryPlanner()
        plan = planner.plan_condition(
            condition_slug="minimal",
            display_name="Minimal Condition",
        )
        assert len(plan.queries) > 5  # still generates core queries


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Deduplication
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestDeduplication:
    def test_removes_duplicates_by_pmid(self):
        from sozo_generator.evidence.deduper import deduplicate_evidence_items

        items = [
            _make_item(pmid="11111111", relevance=3.0),
            _make_item(pmid="11111111", relevance=7.0),
            _make_item(pmid="22222222", relevance=5.0),
        ]
        result = deduplicate_evidence_items(items)
        assert len(result.unique_items) == 2
        assert result.duplicates_removed == 1

    def test_keeps_higher_score(self):
        from sozo_generator.evidence.deduper import deduplicate_evidence_items

        items = [
            _make_item(pmid="11111111", relevance=3.0, title="Low"),
            _make_item(pmid="11111111", relevance=7.0, title="High"),
        ]
        result = deduplicate_evidence_items(items)
        kept = [i for i in result.unique_items if i.pmid == "11111111"]
        assert len(kept) == 1
        assert kept[0].relevance_score == 7.0

    def test_items_without_pmid_kept(self):
        from sozo_generator.evidence.deduper import deduplicate_evidence_items

        items = [
            _make_item(pmid=None, title="No PMID A"),
            _make_item(pmid=None, title="No PMID B"),
            _make_item(pmid="11111111"),
        ]
        result = deduplicate_evidence_items(items)
        assert len(result.unique_items) == 3
        assert result.duplicates_removed == 0

    def test_no_duplicates(self):
        from sozo_generator.evidence.deduper import deduplicate_evidence_items

        items = [
            _make_item(pmid="11111111"),
            _make_item(pmid="22222222"),
        ]
        result = deduplicate_evidence_items(items)
        assert len(result.unique_items) == 2
        assert result.duplicates_removed == 0
        assert result.merge_log == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Ranker
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestRanker:
    def test_rank_returns_sorted_list(self):
        from sozo_generator.evidence.ranker import rank_evidence_items

        items = [
            _make_item(pmid="1", level=EvidenceLevel.LOW, year=2018),
            _make_item(pmid="2", level=EvidenceLevel.HIGHEST, year=2024),
            _make_item(pmid="3", level=EvidenceLevel.MEDIUM, year=2022),
        ]
        ranked = rank_evidence_items(items, top_n=10, current_year=2024)
        assert len(ranked) == 3
        # Highest level + recent year should rank first
        assert ranked[0].pmid == "2"

    def test_top_n_limits(self):
        from sozo_generator.evidence.ranker import rank_evidence_items

        items = [_make_item(pmid=str(i)) for i in range(20)]
        ranked = rank_evidence_items(items, top_n=5)
        assert len(ranked) == 5

    def test_empty_input(self):
        from sozo_generator.evidence.ranker import rank_evidence_items

        ranked = rank_evidence_items([], top_n=10)
        assert ranked == []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Clusterer
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestClusterer:
    def test_cluster_groups_by_category(self):
        from sozo_generator.evidence.clusterer import cluster_into_bundles

        items = [
            _make_item(
                pmid="1",
                title="Safety profile of tDCS adverse events",
                key_finding="Safety and tolerability study",
            ),
            _make_item(
                pmid="2",
                title="Pathophysiology of neural degeneration",
                key_finding="Mechanism and etiology",
            ),
            _make_item(
                pmid="3",
                title="Contraindication seizure risk with implants",
                key_finding="Precaution regarding pacemaker",
            ),
        ]
        bundles = cluster_into_bundles(items, condition_slug="test")
        assert len(bundles) >= 1
        categories = {b.category for b in bundles}
        # At least safety and pathophysiology should appear
        assert len(categories) >= 2

    def test_cluster_empty_input(self):
        from sozo_generator.evidence.clusterer import cluster_into_bundles

        bundles = cluster_into_bundles([], condition_slug="test")
        assert bundles == []

    def test_cluster_assigns_confidence(self):
        from sozo_generator.evidence.clusterer import cluster_into_bundles

        items = [
            _make_item(
                pmid=str(i),
                level=EvidenceLevel.HIGH,
                title="pathophysiology mechanism study",
                key_finding="pathophysiology mechanism",
            )
            for i in range(5)
        ]
        bundles = cluster_into_bundles(items, condition_slug="test")
        assert len(bundles) >= 1
        # With 5 HIGH items, confidence should be at least HIGH or MEDIUM
        patho_bundles = [
            b for b in bundles if b.category == ClaimCategory.PATHOPHYSIOLOGY
        ]
        if patho_bundles:
            assert patho_bundles[0].confidence in (
                ConfidenceLabel.HIGH,
                ConfidenceLabel.MEDIUM,
            )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Contradiction detection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestContradictionDetector:
    def test_detect_relation_conflict(self):
        from sozo_generator.evidence.contradiction import detect_contradictions

        items = [
            _make_item(pmid="1", relation=EvidenceRelation.SUPPORTS, title="Pro"),
            _make_item(pmid="2", relation=EvidenceRelation.CONTRADICTS, title="Con"),
        ]
        bundle = _make_bundle(items=items)
        result = detect_contradictions(bundle)
        assert result.has_contradictions is True
        assert result.contradiction_count >= 1

    def test_detect_direction_conflict(self):
        from sozo_generator.evidence.contradiction import detect_contradictions

        items = [
            _make_item(
                pmid="1",
                key_finding="tDCS was effective and showed significant improvement",
            ),
            _make_item(
                pmid="2",
                key_finding="tDCS showed no effect and no significant difference",
            ),
        ]
        bundle = _make_bundle(items=items)
        result = detect_contradictions(bundle)
        assert result.has_contradictions is True

    def test_no_contradictions(self):
        from sozo_generator.evidence.contradiction import detect_contradictions

        items = [
            _make_item(pmid="1", relation=EvidenceRelation.SUPPORTS),
            _make_item(pmid="2", relation=EvidenceRelation.SUPPORTS),
        ]
        bundle = _make_bundle(items=items)
        result = detect_contradictions(bundle)
        assert result.has_contradictions is False
        assert result.contradiction_count == 0

    def test_empty_bundle(self):
        from sozo_generator.evidence.contradiction import detect_contradictions

        bundle = _make_bundle()
        result = detect_contradictions(bundle)
        assert result.has_contradictions is False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SnapshotManager
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestSnapshotManager:
    def test_create_and_load_roundtrip(self, tmp_path):
        from sozo_generator.evidence.snapshots import SnapshotManager

        mgr = SnapshotManager(tmp_path / "snapshots")
        bundle = _make_bundle(
            items=[_make_item(pmid="11111111", title="Test article")]
        )
        manifest = mgr.create_snapshot(
            condition_slug="test",
            bundles=[bundle],
            search_queries=["query1", "query2"],
            notes="test snapshot",
        )
        assert manifest.snapshot_id.startswith("snap-test-")
        assert manifest.total_articles == 1
        assert manifest.content_hash != ""

        # Load it back
        loaded = mgr.load_snapshot(manifest.snapshot_id)
        assert loaded.snapshot_id == manifest.snapshot_id
        assert loaded.condition_slug == "test"
        assert len(loaded.bundles) == 1
        assert loaded.content_hash == manifest.content_hash

    def test_list_snapshots(self, tmp_path):
        from sozo_generator.evidence.snapshots import SnapshotManager

        mgr = SnapshotManager(tmp_path / "snapshots")
        mgr.create_snapshot(
            condition_slug="test",
            bundles=[],
            search_queries=[],
        )
        ids = mgr.list_snapshots("test")
        assert len(ids) == 1
        assert ids[0].startswith("snap-test-")

    def test_list_snapshots_empty(self, tmp_path):
        from sozo_generator.evidence.snapshots import SnapshotManager

        mgr = SnapshotManager(tmp_path / "snapshots")
        assert mgr.list_snapshots("nonexistent") == []

    def test_latest_snapshot(self, tmp_path):
        from sozo_generator.evidence.snapshots import SnapshotManager

        mgr = SnapshotManager(tmp_path / "snapshots")
        mgr.create_snapshot(condition_slug="test", bundles=[], search_queries=[])
        latest = mgr.latest_snapshot("test")
        assert latest is not None
        assert latest.condition_slug == "test"

    def test_latest_snapshot_none(self, tmp_path):
        from sozo_generator.evidence.snapshots import SnapshotManager

        mgr = SnapshotManager(tmp_path / "snapshots")
        assert mgr.latest_snapshot("empty") is None

    def test_load_invalid_id_raises(self, tmp_path):
        from sozo_generator.evidence.snapshots import SnapshotManager

        mgr = SnapshotManager(tmp_path / "snapshots")
        with pytest.raises(ValueError, match="Invalid snapshot ID"):
            mgr.load_snapshot("bad-format")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BundleStore
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class TestBundleStore:
    def test_save_and_load_roundtrip(self, tmp_path):
        from sozo_generator.evidence.bundles import BundleStore

        store = BundleStore(tmp_path / "bundles")
        bundle = _make_bundle(
            bundle_id="test_patho",
            condition_slug="parkinsons",
            items=[_make_item(pmid="12345678")],
        )
        path = store.save(bundle)
        assert path.exists()

        loaded = store.load("test_patho", condition_slug="parkinsons")
        assert loaded.bundle_id == "test_patho"
        assert loaded.condition_slug == "parkinsons"
        assert len(loaded.items) == 1

    def test_load_not_found_raises(self, tmp_path):
        from sozo_generator.evidence.bundles import BundleStore

        store = BundleStore(tmp_path / "bundles")
        with pytest.raises(FileNotFoundError):
            store.load("nonexistent")

    def test_list_bundles(self, tmp_path):
        from sozo_generator.evidence.bundles import BundleStore

        store = BundleStore(tmp_path / "bundles")
        for i in range(3):
            b = _make_bundle(
                bundle_id=f"b{i}",
                condition_slug="test",
            )
            store.save(b)
        ids = store.list_bundles("test")
        assert len(ids) == 3

    def test_list_bundles_empty(self, tmp_path):
        from sozo_generator.evidence.bundles import BundleStore

        store = BundleStore(tmp_path / "bundles")
        assert store.list_bundles("nothing") == []

    def test_get_all(self, tmp_path):
        from sozo_generator.evidence.bundles import BundleStore

        store = BundleStore(tmp_path / "bundles")
        for i in range(2):
            store.save(
                _make_bundle(bundle_id=f"b{i}", condition_slug="test")
            )
        all_bundles = store.get_all("test")
        assert len(all_bundles) == 2
