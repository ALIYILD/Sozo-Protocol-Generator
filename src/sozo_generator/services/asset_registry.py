"""Central asset registry for the SOZO long-document production pipeline.

This module provides :class:`AssetRegistry`, the single source of truth for all
non-text assets (tables, figures, charts, images, diagrams, etc.) generated
during a document build run.  It handles the full asset lifecycle:

    pending → generating → generated → validated

and assigns human-readable numbering labels (``Table 1``, ``Figure 1``, …)
during the finalization phase.  The registry can be persisted to JSON for
resumability across interrupted runs.

Module-level helpers :func:`get_asset_registry` and :func:`reset_registry`
manage an optional global singleton for convenience.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from sozo_generator.schemas.canonical import AssetRecord

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Asset types that count as "figures" for the purposes of sequential numbering.
_FIGURE_TYPES = frozenset(
    {"figure", "chart", "image", "diagram", "topomap", "montage", "timeline", "flowchart"}
)

# Statuses that qualify an asset for numbering.
_NUMBERED_STATUSES = frozenset({"generated", "validated"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    """Generate a new random asset ID."""
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class AssetRegistry:
    """Central registry for all document assets (tables, figures, charts, images).

    Tracks asset lifecycle: pending → generating → generated → validated.
    Assigns numbering labels (Table 1, Figure 1, etc.) during finalization.
    Persists to JSON for resumability.
    """

    def __init__(self, registry_path: Optional[str] = None) -> None:
        """Initialise the registry, loading from *registry_path* if it exists.

        Args:
            registry_path: Path to JSON file for persistence.  If ``None``,
                operates in-memory only.
        """
        self._records: dict[str, AssetRecord] = {}
        self._registry_path = registry_path
        if registry_path and os.path.exists(registry_path):
            self.load(registry_path)

    # ------------------------------------------------------------------
    # Registration & retrieval
    # ------------------------------------------------------------------

    def register(
        self,
        asset_type: str,
        condition_slug: str,
        section_target: str,
        renderer_type: str,
        source_data: dict,
        caption: Optional[str] = None,
        caption_short: Optional[str] = None,
        variant_tags: Optional[list[str]] = None,
        asset_id: Optional[str] = None,
    ) -> AssetRecord:
        """Register a new asset and return the created :class:`AssetRecord`.

        A unique *asset_id* is auto-generated when not provided.  The record
        is stored in ``status="pending"`` and both ``created_at`` and
        ``updated_at`` are set to the current UTC time.

        Args:
            asset_type: One of the :data:`AssetType` literals.
            condition_slug: Condition identifier (e.g. ``"tbi"``).
            section_target: Section ID where the asset appears.
            renderer_type: Renderer key (e.g. ``"table_builder"``).
            source_data: Input data dict passed verbatim to the renderer.
            caption: Long caption text (optional).
            caption_short: Short caption for lists/TOC (optional).
            variant_tags: Optional list of variant tags.
            asset_id: Explicit ID; auto-generated if omitted.

        Returns:
            The newly created :class:`AssetRecord`.

        Raises:
            ValueError: If *asset_id* is already registered.
        """
        if asset_id is None:
            asset_id = _new_id()

        if asset_id in self._records:
            raise ValueError(f"Asset already registered: {asset_id!r}")

        now = _now_iso()
        record = AssetRecord(
            asset_id=asset_id,
            asset_type=asset_type,
            condition_slug=condition_slug,
            section_target=section_target,
            renderer_type=renderer_type,
            source_data=source_data,
            caption=caption,
            caption_short=caption_short,
            variant_tags=variant_tags or [],
            status="pending",
            created_at=now,
            updated_at=now,
        )
        self._records[asset_id] = record
        return record

    def get(self, asset_id: str) -> Optional[AssetRecord]:
        """Return the :class:`AssetRecord` for *asset_id*, or ``None``."""
        return self._records.get(asset_id)

    def resolve_by_id(self, asset_id: str) -> Optional[AssetRecord]:
        """Look up an asset by *asset_id*.  Used during document assembly.

        Alias for :meth:`get`; provided for semantic clarity at call sites.
        """
        return self._records.get(asset_id)

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def update_status(
        self,
        asset_id: str,
        status: str,
        output_path: Optional[str] = None,
        error_message: Optional[str] = None,
        checksum: Optional[str] = None,
    ) -> AssetRecord:
        """Update the status of an asset and optionally its output metadata.

        Refreshes ``updated_at`` to the current UTC time.

        Args:
            asset_id: ID of the asset to update.
            status: New :data:`AssetStatus` value.
            output_path: File-system path to the rendered output (optional).
            error_message: Human-readable error string for ``"failed"`` status.
            checksum: Pre-computed SHA-256 hex digest (optional).

        Returns:
            The updated :class:`AssetRecord`.

        Raises:
            KeyError: If *asset_id* is not registered.
        """
        record = self._require(asset_id)
        record.status = status  # type: ignore[assignment]
        record.updated_at = _now_iso()
        if output_path is not None:
            record.output_path = output_path
        if error_message is not None:
            record.error_message = error_message
        if checksum is not None:
            record.checksum = checksum
        return record

    def update_caption(
        self,
        asset_id: str,
        caption: str,
        caption_short: Optional[str] = None,
    ) -> AssetRecord:
        """Update the caption fields of an asset after generation.

        Refreshes ``updated_at`` to the current UTC time.

        Args:
            asset_id: ID of the asset to update.
            caption: Long caption text.
            caption_short: Short caption (optional).

        Returns:
            The updated :class:`AssetRecord`.

        Raises:
            KeyError: If *asset_id* is not registered.
        """
        record = self._require(asset_id)
        record.caption = caption
        if caption_short is not None:
            record.caption_short = caption_short
        record.updated_at = _now_iso()
        return record

    # ------------------------------------------------------------------
    # Numbering
    # ------------------------------------------------------------------

    def finalize_numbering(self) -> None:
        """Assign sequential numbering labels to all generated assets.

        Only assets with ``status`` of ``"generated"`` or ``"validated"`` are
        numbered.  The two numbering sequences are:

        - **Tables** — ``"Table 1"``, ``"Table 2"``, …  (asset_type == ``"table"``)
        - **Figures** — ``"Figure 1"``, ``"Figure 2"``, …  (all other asset types)

        Assets are ordered deterministically by
        ``(section_target, asset_type, created_at)`` before numbering.

        Updates ``numbering_slot`` (1-based integer position within the
        sequence) and ``numbering_label`` (e.g. ``"Figure 3"``) on each
        qualifying record.  ``updated_at`` is refreshed for each numbered
        record.
        """
        eligible = [
            r for r in self._records.values() if r.status in _NUMBERED_STATUSES
        ]
        # Deterministic ordering
        eligible.sort(
            key=lambda r: (r.section_target, r.asset_type, r.created_at)
        )

        table_counter = 0
        figure_counter = 0
        now = _now_iso()

        for record in eligible:
            if record.asset_type == "table":
                table_counter += 1
                record.numbering_slot = table_counter
                record.numbering_label = f"Table {table_counter}"
            else:
                figure_counter += 1
                record.numbering_slot = figure_counter
                record.numbering_label = f"Figure {figure_counter}"
            record.updated_at = now

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_all(self) -> list[AssetRecord]:
        """Return all registered assets in insertion order."""
        return list(self._records.values())

    def get_by_condition(self, condition_slug: str) -> list[AssetRecord]:
        """Return all assets whose ``condition_slug`` matches *condition_slug*."""
        return [r for r in self._records.values() if r.condition_slug == condition_slug]

    def get_by_section(self, section_target: str) -> list[AssetRecord]:
        """Return all assets whose ``section_target`` matches *section_target*."""
        return [r for r in self._records.values() if r.section_target == section_target]

    def get_by_type(self, asset_type: str) -> list[AssetRecord]:
        """Return all assets whose ``asset_type`` matches *asset_type*."""
        return [r for r in self._records.values() if r.asset_type == asset_type]

    def get_by_status(self, status: str) -> list[AssetRecord]:
        """Return all assets with the given *status*."""
        return [r for r in self._records.values() if r.status == status]

    def get_missing_assets(self) -> list[AssetRecord]:
        """Return assets whose status is ``"failed"`` or ``"missing"``."""
        return [r for r in self._records.values() if r.status in ("failed", "missing")]

    def get_pending_assets(self) -> list[AssetRecord]:
        """Return assets whose status is ``"pending"``."""
        return [r for r in self._records.values() if r.status == "pending"]

    # ------------------------------------------------------------------
    # Checksum
    # ------------------------------------------------------------------

    def checksum_asset(self, asset_id: str) -> Optional[str]:
        """Compute the SHA-256 checksum of the asset's output file.

        Reads ``output_path`` from the record, hashes the file contents, stores
        the hex digest in ``record.checksum``, and returns it.  Returns
        ``None`` if no ``output_path`` is set or the file does not exist.

        Args:
            asset_id: ID of the asset to checksum.

        Raises:
            KeyError: If *asset_id* is not registered.
        """
        record = self._require(asset_id)
        if not record.output_path:
            logger.warning("checksum_asset: no output_path set for %r", asset_id)
            return None
        if not os.path.exists(record.output_path):
            logger.warning(
                "checksum_asset: output file not found for %r: %s",
                asset_id,
                record.output_path,
            )
            return None

        sha = hashlib.sha256()
        with open(record.output_path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                sha.update(chunk)

        digest = sha.hexdigest()
        record.checksum = digest
        record.updated_at = _now_iso()
        return digest

    # ------------------------------------------------------------------
    # Condition reset
    # ------------------------------------------------------------------

    def reset_condition(self, condition_slug: str) -> None:
        """Remove all assets for *condition_slug* (for reruns).

        Args:
            condition_slug: Condition whose assets should be removed.
        """
        ids_to_remove = [
            aid
            for aid, r in self._records.items()
            if r.condition_slug == condition_slug
        ]
        for aid in ids_to_remove:
            del self._records[aid]
        logger.debug(
            "reset_condition: removed %d assets for condition %r",
            len(ids_to_remove),
            condition_slug,
        )

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Optional[str] = None) -> str:
        """Serialise the registry to JSON and write to *path*.

        If *path* is ``None``, falls back to the ``registry_path`` supplied at
        construction.  Raises :class:`ValueError` if neither is available.

        Args:
            path: Destination file path (optional override).

        Returns:
            The resolved file path that was written.

        Raises:
            ValueError: If no path is available.
        """
        resolved = path or self._registry_path
        if not resolved:
            raise ValueError(
                "No path supplied and no registry_path configured at construction."
            )

        parent = os.path.dirname(resolved)
        if parent:
            os.makedirs(parent, exist_ok=True)

        with open(resolved, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2, ensure_ascii=False)

        logger.debug("Registry saved to %s (%d records)", resolved, len(self._records))
        return resolved

    def load(self, path: str) -> None:
        """Load registry records from a JSON file, merging into existing state.

        Unknown or malformed records are skipped with a warning rather than
        raising an exception.  The internal ``_registry_path`` is updated to
        *path*.

        Args:
            path: Source file path.
        """
        if not os.path.exists(path):
            logger.warning("load: registry file not found, skipping: %s", path)
            return

        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("load: failed to read registry from %s: %s", path, exc)
            return

        self._registry_path = path

        raw_records: dict = data.get("records", {})
        loaded = 0
        for asset_id, record_dict in raw_records.items():
            try:
                self._records[asset_id] = AssetRecord(**record_dict)
                loaded += 1
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "load: skipping malformed record %r: %s", asset_id, exc
                )

        logger.debug("Registry loaded from %s (%d records)", path, loaded)

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serialise the registry to a plain Python dict.

        The returned structure is JSON-serialisable without further processing.
        """
        return {
            "records": {
                aid: record.model_dump()
                for aid, record in self._records.items()
            },
            "meta": {
                "total": len(self._records),
                "exported_at": _now_iso(),
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AssetRegistry":
        """Deserialise a registry from a plain dict previously produced by :meth:`to_dict`.

        Args:
            data: Dict with a ``"records"`` key containing asset dicts.

        Returns:
            A new :class:`AssetRegistry` populated from *data*.
        """
        instance = cls()
        raw_records: dict = data.get("records", {})
        for asset_id, record_dict in raw_records.items():
            try:
                instance._records[asset_id] = AssetRecord(**record_dict)
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "from_dict: skipping malformed record %r: %s", asset_id, exc
                )
        return instance

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        """Return summary statistics for the registry.

        Returns a dict with keys:

        - ``total`` — total number of registered assets
        - ``by_status`` — mapping of status → count
        - ``by_type`` — mapping of asset_type → count
        """
        by_status: dict[str, int] = {}
        by_type: dict[str, int] = {}

        for record in self._records.values():
            by_status[record.status] = by_status.get(record.status, 0) + 1
            by_type[record.asset_type] = by_type.get(record.asset_type, 0) + 1

        return {
            "total": len(self._records),
            "by_status": by_status,
            "by_type": by_type,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require(self, asset_id: str) -> AssetRecord:
        """Return the record for *asset_id* or raise :class:`KeyError`."""
        try:
            return self._records[asset_id]
        except KeyError:
            raise KeyError(f"Asset not found in registry: {asset_id!r}") from None


# ---------------------------------------------------------------------------
# Global singleton helpers
# ---------------------------------------------------------------------------

_global_registry: Optional[AssetRegistry] = None


def get_asset_registry(path: Optional[str] = None) -> AssetRegistry:
    """Get or create the global :class:`AssetRegistry` singleton.

    On first call, a new registry is created (optionally backed by *path*).
    Subsequent calls ignore *path* and return the existing instance.

    Args:
        path: Optional JSON persistence path for first-time initialisation.

    Returns:
        The global :class:`AssetRegistry` instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = AssetRegistry(path)
    return _global_registry


def reset_registry() -> None:
    """Reset the global registry singleton.

    After calling this, the next :func:`get_asset_registry` call will create
    a fresh instance.  Primarily intended for use in tests.
    """
    global _global_registry
    _global_registry = None
