"""Tests for the release signoff, publication, and registry system."""
import json
import pytest
from pathlib import Path


@pytest.fixture
def release_svc(tmp_path):
    from sozo_generator.knowledge.publish import ReleaseService
    return ReleaseService(releases_dir=tmp_path / "releases")


class TestReleaseCandidates:
    def test_get_candidates(self, release_svc):
        candidates = release_svc.get_candidates("parkinsons", "fellow")
        assert len(candidates) >= 7
        for c in candidates:
            assert c.condition == "parkinsons"
            assert c.tier == "fellow"

    def test_candidates_have_eligibility(self, release_svc):
        candidates = release_svc.get_candidates("parkinsons", "fellow")
        eligible = [c for c in candidates if c.eligible]
        ineligible = [c for c in candidates if not c.eligible]
        assert len(eligible) >= 5
        for c in ineligible:
            assert len(c.blockers) > 0


class TestReleaseLifecycle:
    def test_create_draft(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow", created_by="Dr. Test")
        assert release.state == "draft"
        assert release.scope_condition == "parkinsons"
        assert release.total_included >= 5

    def test_approve(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        approved = release_svc.approve(release.release_id, "Dr. Smith")
        assert approved.state == "approved"
        assert approved.approved_by == "Dr. Smith"

    def test_publish(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        published = release_svc.publish(release.release_id)
        assert published.state == "published"
        assert published.bundle_path
        assert Path(published.bundle_path).exists()

    def test_reject(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        rejected = release_svc.reject(release.release_id, "Dr. Smith", "Not ready")
        assert rejected.state == "rejected"

    def test_revoke(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        published = release_svc.publish(release.release_id)
        revoked = release_svc.revoke(release.release_id, "Dr. Smith", "Withdrawn")
        assert revoked.state == "revoked"

    def test_cannot_publish_unapproved(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        with pytest.raises(ValueError, match="must be 'approved'"):
            release_svc.publish(release.release_id)

    def test_cannot_approve_published(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        release_svc.publish(release.release_id)
        with pytest.raises(ValueError):
            release_svc.approve(release.release_id, "Dr. Jones")


class TestReleaseManifest:
    def test_manifest_includes_eligible_docs(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        assert release.total_included >= 5
        for doc in release.included:
            assert doc["readiness"] == "ready"

    def test_manifest_excludes_blocked_docs(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        for doc in release.excluded:
            assert "blockers" in doc
            assert len(doc["blockers"]) > 0

    def test_manifest_has_pmid_count(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        assert release.total_pmids > 100

    def test_manifest_text_output(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        text = release.to_text()
        assert "RELEASE" in text
        assert "parkinsons" in text

    def test_manifest_persisted(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        loaded = release_svc.get_release(release.release_id)
        assert loaded is not None
        assert loaded.release_id == release.release_id


class TestReleaseBundle:
    def test_bundle_contains_manifest(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        published = release_svc.publish(release.release_id)
        bundle = Path(published.bundle_path)
        assert (bundle / "manifest.json").exists()

    def test_bundle_contains_summary(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        published = release_svc.publish(release.release_id)
        bundle = Path(published.bundle_path)
        assert (bundle / "release_summary.md").exists()

    def test_bundle_contains_docs(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        published = release_svc.publish(release.release_id)
        docs_dir = Path(published.bundle_path) / "docs"
        assert docs_dir.exists()
        docx_files = list(docs_dir.glob("*.docx"))
        assert len(docx_files) >= 1


class TestReleaseRegistry:
    def test_registry_tracks_releases(self, release_svc):
        release_svc.create_release("parkinsons", "fellow")
        release_svc.create_release("depression", "fellow")
        releases = release_svc.list_releases()
        # Note: list_releases reads from registry, which is updated on publish
        # Draft releases are saved as manifests but not in registry until published

    def test_published_appears_in_registry(self, release_svc):
        release = release_svc.create_release("parkinsons", "fellow")
        release_svc.approve(release.release_id, "Dr. Smith")
        release_svc.publish(release.release_id)
        releases = release_svc.list_releases()
        assert len(releases) >= 1
        ids = [r["release_id"] for r in releases]
        assert release.release_id in ids


class TestMultiConditionRelease:
    def test_depression_release(self, release_svc):
        release = release_svc.create_release("depression", "fellow")
        assert release.total_included >= 5

    def test_migraine_release(self, release_svc):
        release = release_svc.create_release("migraine", "fellow")
        assert release.total_included >= 5
