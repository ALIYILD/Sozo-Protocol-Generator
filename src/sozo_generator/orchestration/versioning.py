"""
Build versioning — content hashing, version stamps, and manifest persistence.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..schemas.contracts import (
    BuildManifest,
    DocumentBuildEntry,
    FigureManifest,
    QAReport,
    ClaimCitationMap,
)
from ..core.enums import ReviewStatus

logger = logging.getLogger(__name__)

GENERATOR_VERSION = "1.0.0"


def compute_file_hash(file_path: Path) -> str:
    """SHA-256 hash of file content, first 16 hex chars."""
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:16]
    except OSError:
        return ""


def create_build_id(condition_slug: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"build-{condition_slug}-{ts}"


class ManifestWriter:
    """Creates and persists BuildManifest files."""

    def __init__(self, manifests_dir: Path):
        self.manifests_dir = Path(manifests_dir)
        self.manifests_dir.mkdir(parents=True, exist_ok=True)

    def create_manifest(
        self,
        build_id: str,
        condition_slug: str,
        condition_name: str,
        document_outputs: dict[str, Path],
        evidence_snapshot_id: Optional[str] = None,
        figure_manifest: Optional[FigureManifest] = None,
        qa_summary: Optional[QAReport] = None,
        claim_citation_map: Optional[ClaimCitationMap] = None,
    ) -> BuildManifest:
        """Build a manifest from export results."""
        documents: list[DocumentBuildEntry] = []

        for key, path in document_outputs.items():
            parts = key.split("_", 1)
            tier = parts[0] if len(parts) > 1 else "unknown"
            doc_type = parts[1] if len(parts) > 1 else key

            content_hash = compute_file_hash(path) if path.exists() else ""
            qa_passed = True
            qa_block_count = 0

            if qa_summary:
                doc_issues = [
                    i for i in qa_summary.issues
                    if i.location.startswith(doc_type) or i.category == doc_type
                ]
                qa_block_count = sum(1 for i in doc_issues if i.severity.value == "block")
                qa_passed = qa_block_count == 0

            entry = DocumentBuildEntry(
                document_type=doc_type,
                tier=tier,
                output_path=str(path),
                content_hash=content_hash,
                qa_passed=qa_passed,
                qa_block_count=qa_block_count,
                review_status=ReviewStatus.DRAFT,
            )
            documents.append(entry)

        manifest = BuildManifest(
            build_id=build_id,
            condition_slug=condition_slug,
            condition_name=condition_name,
            generator_version=GENERATOR_VERSION,
            built_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            evidence_snapshot_id=evidence_snapshot_id,
            documents=documents,
            figure_manifest=figure_manifest,
            qa_summary=qa_summary,
            claim_citation_map=claim_citation_map,
            total_documents=len(documents),
            total_passed=sum(1 for d in documents if d.qa_passed),
            total_blocked=sum(1 for d in documents if not d.qa_passed),
        )
        manifest.compute_hash()
        return manifest

    def save_manifest(self, manifest: BuildManifest) -> Path:
        """Write manifest to JSON file."""
        path = self.manifests_dir / f"{manifest.build_id}.json"
        path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        logger.info("Build manifest written: %s", path)
        return path

    def load_manifest(self, build_id: str) -> Optional[BuildManifest]:
        """Load manifest from JSON."""
        path = self.manifests_dir / f"{build_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return BuildManifest(**data)

    def list_manifests(self, condition_slug: Optional[str] = None) -> list[str]:
        """List all manifest build IDs, optionally filtered by condition."""
        ids = []
        for p in sorted(self.manifests_dir.glob("build-*.json")):
            bid = p.stem
            if condition_slug is None or condition_slug in bid:
                ids.append(bid)
        return ids
