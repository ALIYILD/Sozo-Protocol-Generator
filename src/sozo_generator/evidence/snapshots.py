"""
Versioned evidence snapshots — immutable records of evidence state.

Each snapshot captures all bundles, search queries, and article counts at a
point in time. Snapshots are stored as JSON files:
    snapshots_dir/{condition_slug}/snap-{condition_slug}-{YYYYMMDDHHMMSS}.json
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ..schemas.contracts import EvidenceBundle, EvidenceSnapshotManifest

logger = logging.getLogger(__name__)


class SnapshotManager:
    """Manages versioned evidence snapshots on disk."""

    def __init__(self, snapshots_dir: Path) -> None:
        self._snapshots_dir = Path(snapshots_dir)
        self._snapshots_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("SnapshotManager initialized at %s", self._snapshots_dir)

    @property
    def snapshots_dir(self) -> Path:
        return self._snapshots_dir

    def create_snapshot(
        self,
        condition_slug: str,
        bundles: list[EvidenceBundle],
        search_queries: list[str],
        notes: str = "",
    ) -> EvidenceSnapshotManifest:
        """Create and persist a new evidence snapshot.

        Returns the manifest with a computed content hash.
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        snapshot_id = f"snap-{condition_slug}-{timestamp}"

        total_articles = sum(len(b.items) for b in bundles)

        manifest = EvidenceSnapshotManifest(
            snapshot_id=snapshot_id,
            condition_slug=condition_slug,
            pubmed_fetch_date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            total_articles=total_articles,
            bundles=bundles,
            search_queries=search_queries,
            notes=notes,
        )
        manifest.compute_hash()

        # Persist
        condition_dir = self._snapshots_dir / condition_slug
        condition_dir.mkdir(parents=True, exist_ok=True)
        file_path = condition_dir / f"{snapshot_id}.json"

        data = manifest.model_dump(mode="json")
        file_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

        logger.info(
            "Created snapshot %s: %d bundles, %d articles, hash=%s",
            snapshot_id,
            len(bundles),
            total_articles,
            manifest.content_hash,
        )
        return manifest

    def load_snapshot(self, snapshot_id: str) -> EvidenceSnapshotManifest:
        """Load a snapshot by its full ID.

        Extracts condition_slug from the snapshot_id format:
        snap-{condition_slug}-{timestamp}
        """
        # Parse condition_slug from ID: "snap-{slug}-{timestamp}"
        parts = snapshot_id.split("-")
        if len(parts) < 3 or parts[0] != "snap":
            raise ValueError(
                f"Invalid snapshot ID format: {snapshot_id}. "
                f"Expected: snap-{{condition_slug}}-{{timestamp}}"
            )
        # slug is everything between first "snap-" and last "-{timestamp}"
        condition_slug = "-".join(parts[1:-1])

        file_path = self._snapshots_dir / condition_slug / f"{snapshot_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Snapshot not found: {file_path}")

        data = json.loads(file_path.read_text(encoding="utf-8"))
        return EvidenceSnapshotManifest(**data)

    def list_snapshots(self, condition_slug: str) -> list[str]:
        """List all snapshot IDs for a condition, sorted chronologically."""
        condition_dir = self._snapshots_dir / condition_slug
        if not condition_dir.exists():
            return []

        return sorted(
            p.stem
            for p in condition_dir.glob("snap-*.json")
            if p.is_file()
        )

    def latest_snapshot(
        self, condition_slug: str
    ) -> Optional[EvidenceSnapshotManifest]:
        """Load the most recent snapshot for a condition, or None if none exist."""
        snapshot_ids = self.list_snapshots(condition_slug)
        if not snapshot_ids:
            logger.debug("No snapshots found for %s", condition_slug)
            return None

        latest_id = snapshot_ids[-1]  # sorted chronologically, last is newest
        return self.load_snapshot(latest_id)
