"""
Release Signoff + Publication Registry + Export Bundle System.

Turns "ready" into "released" through an explicit, auditable workflow:
  draft → reviewed → approved → published
  (with optional rejected / revoked / invalidated)

Usage:
    from sozo_generator.knowledge.publish import ReleaseService

    svc = ReleaseService()
    release = svc.create_release("parkinsons", "fellow")
    svc.approve(release.release_id, "Dr. Smith")
    bundle = svc.publish(release.release_id)
"""
from __future__ import annotations

import hashlib
import json
import logging
import shutil
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ── Models ────────────────────────────────────────────────────────────────


@dataclass
class ReleaseCandidate:
    """One document being considered for release."""
    condition: str
    doc_type: str
    tier: str
    readiness: str = ""
    sections: int = 0
    placeholders: int = 0
    pmids: int = 0
    eligible: bool = False
    blockers: list[str] = field(default_factory=list)


@dataclass
class ReleaseManifest:
    """Frozen record of what is included in a release."""
    release_id: str = ""
    created_at: str = ""
    created_by: str = ""
    scope_condition: str = ""
    scope_tier: str = ""
    state: str = "draft"  # draft, reviewed, approved, published, rejected, revoked, invalidated
    included: list[dict] = field(default_factory=list)
    excluded: list[dict] = field(default_factory=list)
    total_included: int = 0
    total_excluded: int = 0
    total_pmids: int = 0
    approved_by: str = ""
    approved_at: str = ""
    published_at: str = ""
    bundle_path: str = ""
    notes: str = ""

    def __post_init__(self):
        if not self.release_id:
            self.release_id = _uid("rel-")
        if not self.created_at:
            self.created_at = _now()

    def to_dict(self) -> dict:
        return {
            "release_id": self.release_id,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "scope_condition": self.scope_condition,
            "scope_tier": self.scope_tier,
            "state": self.state,
            "total_included": self.total_included,
            "total_excluded": self.total_excluded,
            "total_pmids": self.total_pmids,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at,
            "published_at": self.published_at,
            "bundle_path": self.bundle_path,
            "notes": self.notes,
            "included": self.included,
            "excluded": self.excluded,
        }

    def to_text(self) -> str:
        lines = [
            f"=== RELEASE: {self.release_id} ===",
            f"State: {self.state.upper()}",
            f"Scope: {self.scope_condition}/{self.scope_tier}",
            f"Included: {self.total_included} documents",
            f"Excluded: {self.total_excluded} documents",
            f"Total PMIDs: {self.total_pmids}",
            f"Created by: {self.created_by} at {self.created_at}",
        ]
        if self.approved_by:
            lines.append(f"Approved by: {self.approved_by} at {self.approved_at}")
        if self.published_at:
            lines.append(f"Published at: {self.published_at}")
        if self.bundle_path:
            lines.append(f"Bundle: {self.bundle_path}")
        if self.excluded:
            lines.append(f"\nEXCLUDED ({self.total_excluded}):")
            for ex in self.excluded:
                lines.append(f"  {ex.get('doc_type', '?')}: {', '.join(ex.get('blockers', []))}")
        return "\n".join(lines)


# ── Release Service ──────────────────────────────────────────────────────


class ReleaseService:
    """Manages the release signoff, publication, and registry workflow."""

    def __init__(self, releases_dir: str | Path | None = None):
        self.releases_dir = Path(releases_dir) if releases_dir else Path("outputs/releases")
        self.releases_dir.mkdir(parents=True, exist_ok=True)
        self._registry_path = self.releases_dir / "registry.json"

    def get_candidates(self, condition: str, tier: str = "fellow") -> list[ReleaseCandidate]:
        """Get release candidates for a condition/tier pack."""
        from .cockpit import CockpitService
        svc = CockpitService()
        statuses = [
            s for s in svc._get_all_statuses()
            if s.condition == condition and s.tier == tier
        ]

        candidates = []
        for s in statuses:
            blockers = []
            if s.readiness != "ready":
                blockers.append(f"readiness: {s.readiness}")
            if s.placeholders > 0:
                blockers.append(f"{s.placeholders} placeholders")

            candidates.append(ReleaseCandidate(
                condition=s.condition,
                doc_type=s.doc_type,
                tier=s.tier,
                readiness=s.readiness,
                sections=s.sections,
                placeholders=s.placeholders,
                pmids=s.pmids,
                eligible=len(blockers) == 0,
                blockers=blockers,
            ))

        return candidates

    def create_release(
        self,
        condition: str,
        tier: str = "fellow",
        created_by: str = "operator",
        notes: str = "",
    ) -> ReleaseManifest:
        """Create a draft release for a condition/tier pack."""
        candidates = self.get_candidates(condition, tier)

        included = []
        excluded = []
        total_pmids = 0

        for c in candidates:
            entry = {
                "condition": c.condition,
                "doc_type": c.doc_type,
                "tier": c.tier,
                "readiness": c.readiness,
                "sections": c.sections,
                "pmids": c.pmids,
            }
            if c.eligible:
                included.append(entry)
                total_pmids += c.pmids
            else:
                entry["blockers"] = c.blockers
                excluded.append(entry)

        manifest = ReleaseManifest(
            created_by=created_by,
            scope_condition=condition,
            scope_tier=tier,
            state="draft",
            included=included,
            excluded=excluded,
            total_included=len(included),
            total_excluded=len(excluded),
            total_pmids=total_pmids,
            notes=notes,
        )

        self._save_manifest(manifest)
        return manifest

    def approve(self, release_id: str, approver: str, notes: str = "") -> ReleaseManifest:
        """Approve a release for publication."""
        manifest = self._load_manifest(release_id)
        if not manifest:
            raise ValueError(f"Release not found: {release_id}")
        if manifest.state not in ("draft", "reviewed"):
            raise ValueError(f"Cannot approve release in state '{manifest.state}'")

        manifest.state = "approved"
        manifest.approved_by = approver
        manifest.approved_at = _now()
        if notes:
            manifest.notes = (manifest.notes + "\n" + notes).strip()

        self._save_manifest(manifest)
        logger.info(f"Release {release_id} approved by {approver}")
        return manifest

    def reject(self, release_id: str, rejector: str, reason: str) -> ReleaseManifest:
        """Reject a release."""
        manifest = self._load_manifest(release_id)
        if not manifest:
            raise ValueError(f"Release not found: {release_id}")

        manifest.state = "rejected"
        manifest.approved_by = rejector
        manifest.approved_at = _now()
        manifest.notes = (manifest.notes + f"\nRejected: {reason}").strip()

        self._save_manifest(manifest)
        return manifest

    def publish(self, release_id: str) -> ReleaseManifest:
        """Publish an approved release: generate export bundle and register."""
        manifest = self._load_manifest(release_id)
        if not manifest:
            raise ValueError(f"Release not found: {release_id}")
        if manifest.state != "approved":
            raise ValueError(f"Cannot publish release in state '{manifest.state}' — must be 'approved'")

        # Generate export bundle
        bundle_path = self._generate_bundle(manifest)

        manifest.state = "published"
        manifest.published_at = _now()
        manifest.bundle_path = str(bundle_path)

        self._save_manifest(manifest)
        self._update_registry(manifest)

        logger.info(f"Release {release_id} published → {bundle_path}")
        return manifest

    def revoke(self, release_id: str, revoker: str, reason: str) -> ReleaseManifest:
        """Revoke a previously published release."""
        manifest = self._load_manifest(release_id)
        if not manifest:
            raise ValueError(f"Release not found: {release_id}")

        manifest.state = "revoked"
        manifest.notes = (manifest.notes + f"\nRevoked by {revoker}: {reason}").strip()

        self._save_manifest(manifest)
        self._update_registry(manifest)
        return manifest

    def list_releases(self) -> list[dict]:
        """List all releases from registry."""
        if not self._registry_path.exists():
            return []
        try:
            data = json.loads(self._registry_path.read_text())
            return data.get("releases", [])
        except Exception:
            return []

    def get_release(self, release_id: str) -> Optional[ReleaseManifest]:
        """Load a release manifest."""
        return self._load_manifest(release_id)

    def _generate_bundle(self, manifest: ReleaseManifest) -> Path:
        """Generate the release export bundle directory."""
        bundle_dir = self.releases_dir / manifest.release_id
        bundle_dir.mkdir(parents=True, exist_ok=True)

        docs_dir = bundle_dir / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Copy included document outputs
        for doc in manifest.included:
            # Find the generated DOCX
            condition = doc["condition"]
            doc_type = doc["doc_type"]
            tier = doc["tier"]
            # Try to find the output file
            search_dirs = [
                Path("outputs/documents") / condition / tier,
                Path("outputs/documents") / condition.replace("_", " ").title().replace(" ", "_") / tier.title(),
            ]
            for search_dir in search_dirs:
                if search_dir.exists():
                    for docx_file in search_dir.glob("*.docx"):
                        if doc_type.replace("_", "-") in docx_file.stem.lower() or doc_type.replace("_", "") in docx_file.stem.lower():
                            dest = docs_dir / f"{condition}_{doc_type}_{tier}.docx"
                            shutil.copy2(docx_file, dest)
                            break

        # Write manifest
        manifest_path = bundle_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest.to_dict(), indent=2))

        # Write release summary
        summary_path = bundle_dir / "release_summary.md"
        summary_path.write_text(self._generate_summary_md(manifest))

        return bundle_dir

    def _generate_summary_md(self, manifest: ReleaseManifest) -> str:
        """Generate a Markdown release summary."""
        lines = [
            f"# Release: {manifest.release_id}",
            "",
            f"**Scope**: {manifest.scope_condition} / {manifest.scope_tier}",
            f"**State**: {manifest.state}",
            f"**Created**: {manifest.created_at} by {manifest.created_by}",
        ]
        if manifest.approved_by:
            lines.append(f"**Approved**: {manifest.approved_at} by {manifest.approved_by}")
        if manifest.published_at:
            lines.append(f"**Published**: {manifest.published_at}")

        lines.extend([
            "",
            f"## Included Documents ({manifest.total_included})",
            "",
            "| Condition | Doc Type | Tier | Readiness | PMIDs |",
            "|-----------|----------|------|-----------|-------|",
        ])
        for doc in manifest.included:
            lines.append(
                f"| {doc['condition']} | {doc['doc_type']} | {doc['tier']} | "
                f"{doc['readiness']} | {doc['pmids']} |"
            )

        if manifest.excluded:
            lines.extend([
                "",
                f"## Excluded Documents ({manifest.total_excluded})",
                "",
            ])
            for ex in manifest.excluded:
                lines.append(f"- **{ex['doc_type']}**: {', '.join(ex.get('blockers', []))}")

        if manifest.notes:
            lines.extend(["", "## Notes", "", manifest.notes])

        return "\n".join(lines)

    def _save_manifest(self, manifest: ReleaseManifest):
        """Save manifest to disk."""
        path = self.releases_dir / f"{manifest.release_id}.json"
        path.write_text(json.dumps(manifest.to_dict(), indent=2))

    def _load_manifest(self, release_id: str) -> Optional[ReleaseManifest]:
        """Load manifest from disk."""
        path = self.releases_dir / f"{release_id}.json"
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            return ReleaseManifest(**data)
        except Exception:
            return None

    def _update_registry(self, manifest: ReleaseManifest):
        """Update the release registry."""
        registry = {"releases": self.list_releases()}
        # Update or add entry
        found = False
        for i, entry in enumerate(registry["releases"]):
            if entry.get("release_id") == manifest.release_id:
                registry["releases"][i] = {
                    "release_id": manifest.release_id,
                    "scope": f"{manifest.scope_condition}/{manifest.scope_tier}",
                    "state": manifest.state,
                    "included": manifest.total_included,
                    "approved_by": manifest.approved_by,
                    "published_at": manifest.published_at,
                    "bundle_path": manifest.bundle_path,
                }
                found = True
                break
        if not found:
            registry["releases"].append({
                "release_id": manifest.release_id,
                "scope": f"{manifest.scope_condition}/{manifest.scope_tier}",
                "state": manifest.state,
                "included": manifest.total_included,
                "approved_by": manifest.approved_by,
                "published_at": manifest.published_at,
                "bundle_path": manifest.bundle_path,
            })

        self._registry_path.write_text(json.dumps(registry, indent=2))
