"""Tests for production path: pilot metrics, persistence, section diffs, live refresh."""
from __future__ import annotations

import json
import pytest
from pathlib import Path


class TestActivityLogger:
    def test_log_and_retrieve(self, tmp_path):
        from sozo_generator.orchestration.pilot_metrics import ActivityLogger
        al = ActivityLogger(tmp_path / "logs")
        al.log("approve", operator="Dr. A", build_id="b1", condition_slug="parkinsons")
        al.log("reject", operator="Dr. B", build_id="b2", condition_slug="depression")
        events = al.get_events()
        assert len(events) == 2
        assert events[0].action == "approve"
        assert events[1].operator == "Dr. B"

    def test_filter_by_since(self, tmp_path):
        from sozo_generator.orchestration.pilot_metrics import ActivityLogger
        al = ActivityLogger(tmp_path / "logs")
        al.log("approve", operator="Dr. A")
        events = al.get_events(since="2020-01-01")
        assert len(events) == 1

    def test_empty_log(self, tmp_path):
        from sozo_generator.orchestration.pilot_metrics import ActivityLogger
        al = ActivityLogger(tmp_path / "logs")
        assert al.get_events() == []

    def test_compute_metrics(self, tmp_path):
        from sozo_generator.orchestration.pilot_metrics import ActivityLogger
        al = ActivityLogger(tmp_path / "logs")
        al.log("approve", operator="Dr. A", build_id="b1", condition_slug="parkinsons")
        al.log("approve", operator="Dr. A", build_id="b2", condition_slug="depression")
        al.log("reject", operator="Dr. B", build_id="b3", condition_slug="anxiety")
        al.log("flag", operator="Dr. A", build_id="b4")
        al.log("export", build_id="b5")
        al.log("generate", condition_slug="adhd")
        al.log("qa_run")
        al.log("download_report")
        al.log("onboard", condition_slug="narcolepsy")

        m = al.compute_metrics()
        assert m.total_events == 9
        assert m.docs_approved == 2
        assert m.docs_rejected == 1
        assert m.docs_flagged == 1
        assert m.docs_exported == 1
        assert m.docs_generated == 1
        assert m.qa_runs == 1
        assert m.reports_downloaded == 1
        assert m.conditions_onboarded == 1
        assert "Dr. A" in m.unique_operators
        assert "Dr. B" in m.unique_operators
        assert m.by_condition.get("parkinsons", 0) >= 1

    def test_format_markdown(self, tmp_path):
        from sozo_generator.orchestration.pilot_metrics import ActivityLogger
        al = ActivityLogger(tmp_path / "logs")
        al.log("approve", operator="Dr. A", condition_slug="parkinsons")
        m = al.compute_metrics()
        md = al.format_metrics_markdown(m)
        assert "Pilot Metrics" in md
        assert "Documents approved" in md


class TestPersistenceStore:
    def test_json_store_crud(self, tmp_path):
        from sozo_generator.persistence.store import JSONFileStore
        store = JSONFileStore(tmp_path / "store")
        store.save("doc1", {"status": "draft"})
        assert store.exists("doc1")
        assert store.load("doc1") == {"status": "draft"}
        store.save("doc1", {"status": "approved"})
        assert store.load("doc1")["status"] == "approved"
        assert store.delete("doc1")
        assert not store.exists("doc1")
        assert store.load("doc1") is None

    def test_list_keys(self, tmp_path):
        from sozo_generator.persistence.store import JSONFileStore
        store = JSONFileStore(tmp_path / "store")
        store.save("a", {"x": 1})
        store.save("b", {"x": 2})
        store.save("c", {"x": 3})
        keys = store.list_keys()
        assert len(keys) == 3
        assert "a" in keys

    def test_list_keys_with_prefix(self, tmp_path):
        from sozo_generator.persistence.store import JSONFileStore
        store = JSONFileStore(tmp_path / "store")
        store.save("review_1", {"x": 1})
        store.save("review_2", {"x": 2})
        store.save("prov_1", {"x": 3})
        keys = store.list_keys(prefix="review")
        assert len(keys) == 2

    def test_namespaced_store(self, tmp_path):
        from sozo_generator.persistence.store import JSONFileStore, NamespacedStore
        base = JSONFileStore(tmp_path / "store")
        reviews = NamespacedStore(base, "reviews")
        provenance = NamespacedStore(base, "provenance")
        reviews.save("build1", {"status": "approved"})
        provenance.save("build1", {"mode": "standard"})
        assert reviews.load("build1")["status"] == "approved"
        assert provenance.load("build1")["mode"] == "standard"
        assert reviews.list_keys() == ["build1"]
        assert provenance.list_keys() == ["build1"]

    def test_delete_nonexistent(self, tmp_path):
        from sozo_generator.persistence.store import JSONFileStore
        store = JSONFileStore(tmp_path / "store")
        assert store.delete("nonexistent") == False


class TestLiveRefresh:
    def test_cached_fallback(self, tmp_path):
        from sozo_generator.evidence.live_refresh import LiveEvidenceRefresher, EvidenceProvenance
        from sozo_generator.evidence.cache import EvidenceCache
        from sozo_generator.schemas.evidence import ArticleMetadata
        cache = EvidenceCache(tmp_path)
        cache.set("search|test query|20|5", [
            ArticleMetadata(pmid="12345678", title="Cached Article").model_dump()
        ])
        refresher = LiveEvidenceRefresher(cache_dir=tmp_path)
        result = refresher.refresh("test query", condition_slug="test")
        assert result.provenance == EvidenceProvenance.CACHED
        assert result.cached_count == 1

    def test_unavailable_when_no_cache(self, tmp_path):
        from sozo_generator.evidence.live_refresh import LiveEvidenceRefresher, EvidenceProvenance
        refresher = LiveEvidenceRefresher(cache_dir=tmp_path)
        result = refresher.refresh("nonexistent query", condition_slug="test")
        assert result.provenance == EvidenceProvenance.UNAVAILABLE
        assert len(result.articles) == 0

    def test_is_live_available_property(self):
        from sozo_generator.evidence.live_refresh import LiveEvidenceRefresher
        refresher = LiveEvidenceRefresher()
        assert isinstance(refresher.is_live_available, bool)

    def test_stale_cache_on_force(self, tmp_path):
        from sozo_generator.evidence.live_refresh import LiveEvidenceRefresher, EvidenceProvenance
        from sozo_generator.evidence.cache import EvidenceCache
        from sozo_generator.schemas.evidence import ArticleMetadata
        cache = EvidenceCache(tmp_path)
        cache.set("search|stale test|20|5", [
            ArticleMetadata(pmid="99999", title="Old Article").model_dump()
        ])
        refresher = LiveEvidenceRefresher(cache_dir=tmp_path)
        result = refresher.refresh("stale test", force=True)
        if not refresher.is_live_available:
            assert result.provenance == EvidenceProvenance.STALE
            assert result.cached_count == 1


class TestSectionDiffIntegration:
    def test_diff_with_revision_engine(self):
        from sozo_generator.schemas.documents import DocumentSpec, SectionContent
        from sozo_generator.schemas.condition import ConditionSchema
        from sozo_generator.core.enums import DocumentType, Tier
        from sozo_generator.generation.revision_engine import RevisionEngine
        from sozo_generator.ai.revision_instruction_builder import RevisionPlan, SectionEdit
        from sozo_generator.qa.revision_diff import RevisionDiffGenerator

        spec = DocumentSpec(
            document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=Tier.FELLOW,
            condition_slug="test",
            condition_name="Test",
            title="Test Doc",
            sections=[
                SectionContent(section_id="overview", title="Overview",
                               content="This treatment is proven effective."),
                SectionContent(section_id="safety", title="Safety",
                               content="Standard safety notes."),
                SectionContent(section_id="remove_me", title="Remove Me",
                               content="Will be removed."),
            ],
        )
        condition = ConditionSchema(slug="test", display_name="Test", icd10="X00")
        plan = RevisionPlan(
            document_id="test",
            condition_slug="test",
            section_edits={"overview": SectionEdit(section_id="overview", action="soften")},
            sections_to_remove=["remove_me"],
        )
        engine = RevisionEngine()
        revised, summary = engine.apply_revision(spec, plan, condition)
        differ = RevisionDiffGenerator()
        diff = differ.generate_diff(spec, revised)
        assert diff.total_modified >= 1
        assert diff.total_removed >= 1
        assert diff.summary != ""

    def test_diff_evidence_revision(self, parkinsons_condition):
        from sozo_generator.generation.revision_engine import RevisionEngine
        from sozo_generator.qa.revision_diff import RevisionDiffGenerator
        from sozo_generator.content.assembler import ContentAssembler
        from sozo_generator.schemas.documents import DocumentSpec
        from sozo_generator.core.enums import DocumentType, Tier

        assembler = ContentAssembler()
        sections = assembler.assemble(
            parkinsons_condition, DocumentType.EVIDENCE_BASED_PROTOCOL, Tier.FELLOW
        )
        spec = DocumentSpec(
            document_type=DocumentType.EVIDENCE_BASED_PROTOCOL,
            tier=Tier.FELLOW,
            condition_slug="parkinsons",
            condition_name="Parkinson's Disease",
            title="Test",
            sections=sections,
        )
        engine = RevisionEngine()
        revised, summary = engine.apply_evidence_revision(
            spec, parkinsons_condition, recency_years=5
        )
        differ = RevisionDiffGenerator()
        diff = differ.generate_diff(spec, revised)
        assert diff.summary != ""
        assert len(diff.section_diffs) >= 1


class TestDeploymentSmoke:
    def test_streamlit_app_syntax(self):
        import ast
        with open("app.py") as f:
            ast.parse(f.read())

    def test_all_source_modules_import(self):
        import importlib
        failures = []
        src = Path("src/sozo_generator")
        for py_file in sorted(src.rglob("*.py")):
            if py_file.name == "__init__.py":
                continue
            module_path = (
                str(py_file.relative_to("src")).replace("/", ".").replace(".py", "")
            )
            try:
                importlib.import_module(module_path)
            except Exception as e:
                failures.append(f"{module_path}: {e}")
        assert failures == [], f"Import failures: {failures}"
