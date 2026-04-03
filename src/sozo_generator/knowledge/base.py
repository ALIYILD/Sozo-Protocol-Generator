"""
KnowledgeBase — unified query interface for the SOZO knowledge system.

Loads all knowledge objects, validates cross-references, and provides
query methods for the generation pipeline.

Usage:
    from sozo_generator.knowledge.base import KnowledgeBase

    kb = KnowledgeBase()
    kb.load_all()

    condition = kb.get_condition("parkinsons")
    modalities = kb.get_modalities_for_condition("parkinsons")
    assessments = kb.get_assessments_for_condition("parkinsons")
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .loader import (
    load_conditions,
    load_modalities,
    load_assessments,
    load_brain_targets,
    load_evidence_maps,
    load_contraindications,
    load_shared_rules,
    load_blueprints,
    KNOWLEDGE_ROOT,
)
from .linker import validate_links, LinkReport
from .schemas import (
    KnowledgeCondition,
    KnowledgeModality,
    KnowledgeAssessment,
    KnowledgeBrainTarget,
    KnowledgeEvidenceMap,
    KnowledgeContraindication,
    SharedClinicalRule,
)
from .specs import DocumentBlueprint

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """Unified query interface for SOZO clinical knowledge.

    Loads all knowledge objects from YAML files, validates their
    cross-references, and provides query methods for generation.
    """

    def __init__(self, knowledge_dir: str | Path | None = None):
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir else KNOWLEDGE_ROOT
        self.conditions: dict[str, KnowledgeCondition] = {}
        self.modalities: dict[str, KnowledgeModality] = {}
        self.assessments: dict[str, KnowledgeAssessment] = {}
        self.brain_targets: dict[str, KnowledgeBrainTarget] = {}
        self.evidence_maps: list[KnowledgeEvidenceMap] = []
        self.contraindications: dict[str, KnowledgeContraindication] = {}
        self.shared_rules: dict[str, SharedClinicalRule] = {}
        self.blueprints: dict[str, DocumentBlueprint] = {}
        self._loaded = False
        self._link_report: Optional[LinkReport] = None

    def load_all(self) -> None:
        """Load all knowledge objects from YAML files."""
        logger.info(f"Loading knowledge from {self.knowledge_dir}")
        self.conditions = load_conditions(self.knowledge_dir)
        self.modalities = load_modalities(self.knowledge_dir)
        self.assessments = load_assessments(self.knowledge_dir)
        self.brain_targets = load_brain_targets(self.knowledge_dir)
        self.evidence_maps = load_evidence_maps(self.knowledge_dir)
        self.contraindications = load_contraindications(self.knowledge_dir)
        self.shared_rules = load_shared_rules(self.knowledge_dir)
        self.blueprints = load_blueprints()
        self._loaded = True

        logger.info(
            f"Knowledge loaded: {len(self.conditions)} conditions, "
            f"{len(self.modalities)} modalities, {len(self.assessments)} assessments, "
            f"{len(self.brain_targets)} targets, {len(self.evidence_maps)} evidence maps"
        )

    def validate(self) -> LinkReport:
        """Validate all cross-references between knowledge objects."""
        if not self._loaded:
            self.load_all()
        self._link_report = validate_links(
            self.conditions, self.modalities, self.assessments,
            self.brain_targets, self.evidence_maps,
        )
        return self._link_report

    # ── Condition queries ──────────────────────────────────────────────

    def get_condition(self, slug: str) -> Optional[KnowledgeCondition]:
        """Get a condition by slug."""
        return self.conditions.get(slug)

    def list_conditions(self) -> list[str]:
        """List all condition slugs."""
        return sorted(self.conditions.keys())

    def get_modalities_for_condition(self, condition_slug: str) -> list[KnowledgeModality]:
        """Get all modalities applicable to a condition."""
        cond = self.conditions.get(condition_slug)
        if not cond:
            return []
        return [self.modalities[m] for m in cond.applicable_modalities if m in self.modalities]

    def get_assessments_for_condition(self, condition_slug: str) -> list[KnowledgeAssessment]:
        """Get all assessments used for a condition."""
        cond = self.conditions.get(condition_slug)
        if not cond:
            return []
        return [
            self.assessments[a.scale_key]
            for a in cond.assessments
            if a.scale_key in self.assessments
        ]

    def get_targets_for_condition(self, condition_slug: str) -> list[KnowledgeBrainTarget]:
        """Get brain targets relevant to a condition."""
        return [
            t for t in self.brain_targets.values()
            if condition_slug in t.relevant_conditions
        ]

    def get_evidence_map(
        self, condition_slug: str, modality_slug: str
    ) -> Optional[KnowledgeEvidenceMap]:
        """Get the evidence map linking a condition to a modality."""
        for emap in self.evidence_maps:
            if emap.condition_slug == condition_slug and emap.modality_slug == modality_slug:
                return emap
        return None

    def get_contraindications_for_modality(self, modality_slug: str) -> list[KnowledgeContraindication]:
        """Get contraindications that apply to a modality."""
        return [
            c for c in self.contraindications.values()
            if modality_slug in c.modalities or "all" in c.modalities
        ]

    def get_shared_rules(self, category: str = "") -> list[SharedClinicalRule]:
        """Get shared clinical rules, optionally filtered by category."""
        if not category:
            return list(self.shared_rules.values())
        return [r for r in self.shared_rules.values() if r.category == category]

    # ── Blueprint queries ──────────────────────────────────────────────

    def get_blueprint(self, doc_type_slug: str) -> Optional[DocumentBlueprint]:
        """Get a document blueprint by doc type slug."""
        return self.blueprints.get(doc_type_slug)

    def list_blueprints(self) -> list[str]:
        """List all blueprint slugs."""
        return sorted(self.blueprints.keys())

    # ── Summary ────────────────────────────────────────────────────────

    def summary(self) -> dict:
        """Return a summary of loaded knowledge."""
        return {
            "conditions": len(self.conditions),
            "modalities": len(self.modalities),
            "assessments": len(self.assessments),
            "brain_targets": len(self.brain_targets),
            "evidence_maps": len(self.evidence_maps),
            "contraindications": len(self.contraindications),
            "shared_rules": len(self.shared_rules),
            "blueprints": len(self.blueprints),
            "loaded": self._loaded,
            "valid": self._link_report.valid if self._link_report else None,
        }
