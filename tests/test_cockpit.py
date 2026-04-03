"""Tests for the operator cockpit and operational aggregation."""
import pytest


class TestCockpitOverview:
    def test_overview_counts(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        ov = svc.overview()
        assert ov.conditions_count == 16
        assert ov.blueprints_count == 8
        assert ov.total_generation_paths > 200
        assert ov.documents_ready > 0
        assert ov.documents_ready + ov.documents_review_required + ov.documents_incomplete > 0
        assert ov.total_pmids > 0
        assert ov.knowledge_valid is True

    def test_overview_text(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        text = svc.overview().to_text()
        assert "SOZO CLINICAL PLATFORM COCKPIT" in text
        assert "Conditions:" in text
        assert "Documents ready:" in text


class TestConditionsSummary:
    def test_16_conditions(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        summaries = svc.conditions_summary()
        assert len(summaries) == 16

    def test_each_condition_has_docs(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        for cs in svc.conditions_summary():
            assert cs.total_docs >= 7, f"{cs.condition} has too few docs"

    def test_parkinsons_has_evidence(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        pd = next(cs for cs in svc.conditions_summary() if cs.condition == "parkinsons")
        assert pd.total_pmids > 50


class TestBlockers:
    def test_blockers_are_structured(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        blockers = svc.blockers()
        for b in blockers:
            assert b.condition
            assert b.blocker_type
            assert b.summary

    def test_no_incomplete_blockers(self):
        """No documents should be 'incomplete' — all should be ready or review_required."""
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        incomplete = [b for b in svc.blockers() if b.blocker_type == "readiness_incomplete"]
        assert len(incomplete) == 0


class TestPackSummary:
    def test_pd_fellow_pack(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        pack = svc.pack_summary("parkinsons", "fellow")
        assert pack["total"] >= 7
        assert pack["ready"] >= 5

    def test_pd_partners_pack(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        pack = svc.pack_summary("parkinsons", "partners")
        assert pack["total"] >= 7

    def test_all_conditions_have_packs(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        from sozo_generator.knowledge.base import KnowledgeBase
        svc = CockpitService()
        kb = KnowledgeBase()
        kb.load_all()
        for cond in kb.list_conditions():
            pack = svc.pack_summary(cond, "fellow")
            assert pack["total"] >= 1, f"{cond} has no documents"


class TestReleaseReady:
    def test_release_ready_fellow(self):
        from sozo_generator.knowledge.cockpit import CockpitService
        svc = CockpitService()
        ready = svc.release_ready("fellow")
        assert len(ready) > 0
        for doc in ready:
            assert doc.readiness == "ready"
            assert doc.tier == "fellow"
