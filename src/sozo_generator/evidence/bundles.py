"""
Bundle store — persistent storage and retrieval of EvidenceBundles.

Bundles are stored as JSON files organized by condition slug:
    store_dir/{condition_slug}/{bundle_id}.json

Also provides a helper to build SectionEvidenceMap from bundles.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from ..core.enums import ClaimCategory
from ..schemas.contracts import EvidenceBundle, SectionEvidenceMap

logger = logging.getLogger(__name__)

# ── Section ID mapping by document type ──────────────────────────────
# Maps (document_type, ClaimCategory) -> section_id for building SectionEvidenceMap

_SECTION_MAP: dict[str, dict[ClaimCategory, str]] = {
    "clinical_exam": {
        ClaimCategory.PATHOPHYSIOLOGY: "background",
        ClaimCategory.BRAIN_REGIONS: "neuroanatomy",
        ClaimCategory.NETWORK_INVOLVEMENT: "network_assessment",
        ClaimCategory.CLINICAL_PHENOTYPES: "clinical_presentation",
        ClaimCategory.ASSESSMENT_TOOLS: "assessment",
        ClaimCategory.STIMULATION_TARGETS: "treatment_plan",
        ClaimCategory.STIMULATION_PARAMETERS: "treatment_plan",
        ClaimCategory.MODALITY_RATIONALE: "treatment_rationale",
        ClaimCategory.SAFETY: "safety",
        ClaimCategory.CONTRAINDICATIONS: "contraindications",
        ClaimCategory.RESPONDER_CRITERIA: "outcome_monitoring",
        ClaimCategory.INCLUSION_CRITERIA: "eligibility",
        ClaimCategory.EXCLUSION_CRITERIA: "eligibility",
    },
    "evidence_based_protocol": {
        ClaimCategory.PATHOPHYSIOLOGY: "pathophysiology",
        ClaimCategory.BRAIN_REGIONS: "neuroanatomy",
        ClaimCategory.NETWORK_INVOLVEMENT: "network_model",
        ClaimCategory.CLINICAL_PHENOTYPES: "phenotypes",
        ClaimCategory.ASSESSMENT_TOOLS: "outcome_measures",
        ClaimCategory.STIMULATION_TARGETS: "stimulation_protocol",
        ClaimCategory.STIMULATION_PARAMETERS: "stimulation_protocol",
        ClaimCategory.MODALITY_RATIONALE: "modality_rationale",
        ClaimCategory.SAFETY: "safety_monitoring",
        ClaimCategory.CONTRAINDICATIONS: "contraindications",
        ClaimCategory.RESPONDER_CRITERIA: "responder_criteria",
        ClaimCategory.INCLUSION_CRITERIA: "inclusion_criteria",
        ClaimCategory.EXCLUSION_CRITERIA: "exclusion_criteria",
    },
}


class BundleStore:
    """File-backed store for EvidenceBundles, organized by condition slug."""

    def __init__(self, store_dir: Path) -> None:
        self._store_dir = Path(store_dir)
        self._store_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("BundleStore initialized at %s", self._store_dir)

    @property
    def store_dir(self) -> Path:
        return self._store_dir

    def save(self, bundle: EvidenceBundle) -> Path:
        """Save a bundle to disk as JSON. Returns the file path."""
        condition_dir = self._store_dir / bundle.condition_slug
        condition_dir.mkdir(parents=True, exist_ok=True)

        file_path = condition_dir / f"{bundle.bundle_id}.json"
        data = bundle.model_dump(mode="json")
        file_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

        logger.debug("Saved bundle %s -> %s", bundle.bundle_id, file_path)
        return file_path

    def load(self, bundle_id: str, condition_slug: Optional[str] = None) -> EvidenceBundle:
        """Load a bundle by ID.

        If condition_slug is provided, looks directly in that subdirectory.
        Otherwise searches all condition directories.
        """
        if condition_slug:
            file_path = self._store_dir / condition_slug / f"{bundle_id}.json"
            if file_path.exists():
                return self._read_bundle(file_path)
            raise FileNotFoundError(
                f"Bundle {bundle_id} not found in {condition_slug}"
            )

        # Search all condition directories
        for condition_dir in self._store_dir.iterdir():
            if not condition_dir.is_dir():
                continue
            file_path = condition_dir / f"{bundle_id}.json"
            if file_path.exists():
                return self._read_bundle(file_path)

        raise FileNotFoundError(f"Bundle {bundle_id} not found in store")

    def list_bundles(self, condition_slug: str) -> list[str]:
        """List all bundle IDs for a condition."""
        condition_dir = self._store_dir / condition_slug
        if not condition_dir.exists():
            return []

        return [
            p.stem
            for p in sorted(condition_dir.glob("*.json"))
            if p.is_file()
        ]

    def get_all(self, condition_slug: str) -> list[EvidenceBundle]:
        """Load all bundles for a condition."""
        condition_dir = self._store_dir / condition_slug
        if not condition_dir.exists():
            return []

        bundles: list[EvidenceBundle] = []
        for path in sorted(condition_dir.glob("*.json")):
            try:
                bundles.append(self._read_bundle(path))
            except Exception:
                logger.warning("Failed to load bundle from %s", path, exc_info=True)

        logger.debug("Loaded %d bundles for %s", len(bundles), condition_slug)
        return bundles

    @staticmethod
    def build_section_evidence_map(
        condition_slug: str,
        document_type: str,
        tier: str,
        bundles: list[EvidenceBundle],
    ) -> SectionEvidenceMap:
        """Build a SectionEvidenceMap from bundles using document-type section mappings.

        Each bundle is placed under the section ID that corresponds to its
        ClaimCategory for the given document_type.
        """
        section_map = _SECTION_MAP.get(document_type, {})
        section_bundles: dict[str, list[EvidenceBundle]] = {}

        for bundle in bundles:
            section_id = section_map.get(bundle.category, "general")
            section_bundles.setdefault(section_id, []).append(bundle)

        result = SectionEvidenceMap(
            condition_slug=condition_slug,
            document_type=document_type,
            tier=tier,
            section_bundles=section_bundles,
        )

        logger.info(
            "Built SectionEvidenceMap for %s/%s: %d sections from %d bundles",
            condition_slug,
            document_type,
            len(section_bundles),
            len(bundles),
        )
        return result

    # ── Internal ─────────────────────────────────────────────────────

    @staticmethod
    def _read_bundle(path: Path) -> EvidenceBundle:
        """Read and parse a bundle JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return EvidenceBundle(**data)
