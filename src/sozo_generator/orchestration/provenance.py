"""Provenance tracking for generated/revised documents."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class DocumentProvenance:
    """Complete provenance record for one document."""

    document_id: str = ""
    condition_slug: str = ""
    document_type: str = ""
    tier: str = ""
    # Source tracking
    master_profile_version: str = ""  # hash of profile used
    template_family: str = ""  # e.g., "gold_standard", "uploaded", "learned"
    source_template_path: Optional[str] = None
    source_example_docs: list[str] = field(default_factory=list)
    # Revision tracking
    doctor_comments: list[dict] = field(default_factory=list)  # {reviewer, text, timestamp}
    revision_history: list[dict] = field(default_factory=list)  # {action, timestamp, details}
    revision_count: int = 0
    # Evidence
    evidence_bundle_version: Optional[str] = None
    evidence_snapshot_id: Optional[str] = None
    # Generation
    generation_mode: str = ""  # "standard", "template_driven", "profile_guided", "revision"
    generator_version: str = "2.0.0"
    generated_at: str = ""
    # Quality
    qa_passed: bool = False
    qa_block_count: int = 0
    qa_warning_count: int = 0
    consistency_score: Optional[float] = None
    confidence_label: str = ""
    # Lifecycle
    review_status: str = "draft"
    output_path: str = ""

    def add_revision(self, action: str, details: str = "", reviewer: str = "") -> None:
        """Append an entry to the revision history."""
        self.revision_history.append({
            "action": action,
            "timestamp": _now_iso(),
            "details": details,
            "reviewer": reviewer,
        })
        self.revision_count += 1

    def add_comment(self, reviewer: str, text: str) -> None:
        """Record a doctor/reviewer comment."""
        self.doctor_comments.append({
            "reviewer": reviewer,
            "text": text,
            "timestamp": _now_iso(),
        })

    def to_dict(self) -> dict:
        """Serialise to a plain dict suitable for JSON persistence."""
        import dataclasses
        return dataclasses.asdict(self)


class ProvenanceStore:
    """Persists provenance records as JSON files under *store_dir*."""

    def __init__(self, store_dir: Path) -> None:
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ProvenanceStore initialised at %s", self.store_dir)

    # ── Write ──────────────────────────────────────────────────────────

    def save(self, prov: DocumentProvenance) -> Path:
        """Persist a provenance record, returning the file path."""
        path = self._path_for(prov.document_id)
        path.write_text(
            json.dumps(prov.to_dict(), indent=2, default=str),
            encoding="utf-8",
        )
        logger.debug("Saved provenance for %s to %s", prov.document_id, path)
        return path

    # ── Read ───────────────────────────────────────────────────────────

    def load(self, document_id: str) -> Optional[DocumentProvenance]:
        """Load a provenance record by document ID, or ``None`` if missing."""
        path = self._path_for(document_id)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return DocumentProvenance(**data)
        except (json.JSONDecodeError, TypeError, Exception) as exc:
            logger.error("Failed to load provenance from %s: %s", path, exc)
            return None

    # ── Listing ────────────────────────────────────────────────────────

    def list_all(self, condition_slug: str | None = None) -> list[str]:
        """Return document IDs of all stored provenance records.

        Optionally filter by *condition_slug*.
        """
        ids: list[str] = []
        for path in sorted(self.store_dir.glob("*.json")):
            doc_id = path.stem
            if condition_slug is not None:
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if data.get("condition_slug") != condition_slug:
                        continue
                except Exception:
                    continue
            ids.append(doc_id)
        return ids

    def get_revision_history(self, document_id: str) -> list[dict]:
        """Return the revision history list for a document, or ``[]``."""
        prov = self.load(document_id)
        if prov is None:
            return []
        return prov.revision_history

    # ── Internals ──────────────────────────────────────────────────────

    def _path_for(self, document_id: str) -> Path:
        safe = document_id.replace("/", "_").replace("\\", "_")
        return self.store_dir / f"{safe}.json"
