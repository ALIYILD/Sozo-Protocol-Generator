"""
Operator Cockpit — aggregated operational state for the SOZO platform.

Reads persisted artifacts (provenance, readiness, review, promotion, regeneration)
and provides unified views for reviewers and operators.

Usage:
    from sozo_generator.knowledge.cockpit import CockpitService

    svc = CockpitService()
    overview = svc.overview()
    conditions = svc.conditions_summary()
    blockers = svc.blockers()
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── Models ────────────────────────────────────────────────────────────────


@dataclass
class DocStatus:
    """Operational status of one generated document."""
    condition: str
    doc_type: str
    tier: str
    readiness: str = ""
    sections: int = 0
    placeholders: int = 0
    pmids: int = 0
    sections_passing: int = 0
    sections_warning: int = 0
    sections_failing: int = 0
    has_provenance: bool = False
    provenance_path: str = ""


@dataclass
class ReleaseBlocker:
    """One thing preventing a document from release."""
    condition: str
    doc_type: str
    tier: str
    blocker_type: str
    summary: str


@dataclass
class ConditionSummary:
    """Operational summary for one condition."""
    condition: str
    total_docs: int = 0
    ready: int = 0
    review_required: int = 0
    incomplete: int = 0
    total_pmids: int = 0


@dataclass
class CockpitOverview:
    """Platform-wide operational overview."""
    conditions_count: int = 0
    blueprints_count: int = 0
    total_generation_paths: int = 0
    documents_ready: int = 0
    documents_review_required: int = 0
    documents_incomplete: int = 0
    total_pmids: int = 0
    total_sections: int = 0
    promotion_proposals_pending: int = 0
    regeneration_history_count: int = 0
    knowledge_valid: bool = True

    def to_text(self) -> str:
        lines = [
            "╔══════════════════════════════════════════════════════╗",
            "║           SOZO CLINICAL PLATFORM COCKPIT            ║",
            "╚══════════════════════════════════════════════════════╝",
            "",
            f"  Conditions:          {self.conditions_count}",
            f"  Blueprints:          {self.blueprints_count}",
            f"  Generation paths:    {self.total_generation_paths}",
            "",
            f"  Documents ready:     {self.documents_ready}",
            f"  Review required:     {self.documents_review_required}",
            f"  Incomplete:          {self.documents_incomplete}",
            "",
            f"  Total evidence PMIDs: {self.total_pmids}",
            f"  Total sections:       {self.total_sections}",
            "",
            f"  Promotion proposals:  {self.promotion_proposals_pending}",
            f"  Regeneration history: {self.regeneration_history_count}",
            f"  Knowledge valid:      {'YES' if self.knowledge_valid else 'NO'}",
        ]
        return "\n".join(lines)


# ── Cockpit Service ──────────────────────────────────────────────────────


class CockpitService:
    """Aggregates persisted platform state into operational views."""

    def __init__(self):
        self._kb = None
        self._doc_statuses: Optional[list[DocStatus]] = None

    @property
    def kb(self):
        if self._kb is None:
            from .base import KnowledgeBase
            self._kb = KnowledgeBase()
            self._kb.load_all()
        return self._kb

    def overview(self) -> CockpitOverview:
        """Get platform-wide operational overview."""
        ov = CockpitOverview(
            conditions_count=len(self.kb.conditions),
            blueprints_count=len(self.kb.blueprints),
        )

        # Compute total generation paths
        ov.total_generation_paths = ov.conditions_count * ov.blueprints_count * 2  # ×2 tiers

        # Aggregate readiness from batch assembly
        statuses = self._get_all_statuses()
        ov.documents_ready = sum(1 for s in statuses if s.readiness == "ready")
        ov.documents_review_required = sum(1 for s in statuses if s.readiness == "review_required")
        ov.documents_incomplete = sum(1 for s in statuses if s.readiness == "incomplete")
        ov.total_pmids = sum(s.pmids for s in statuses)
        ov.total_sections = sum(s.sections for s in statuses)

        # Promotion proposals
        proposals_dir = Path("outputs/promotion_proposals")
        if proposals_dir.exists():
            ov.promotion_proposals_pending = sum(
                1 for p in proposals_dir.glob("promo-*.json")
                if _read_json_field(p, "status") in ("draft", "pending_review")
            )

        # Regeneration history
        regen_dir = Path("outputs/revision_history")
        if regen_dir.exists():
            ov.regeneration_history_count = len(list(regen_dir.glob("regen-*.json")))

        # Validation
        try:
            from .validate import validate_all
            report = validate_all()
            ov.knowledge_valid = report.passed
        except Exception:
            ov.knowledge_valid = True

        return ov

    def conditions_summary(self) -> list[ConditionSummary]:
        """Get per-condition operational summary."""
        statuses = self._get_all_statuses()
        conditions: dict[str, ConditionSummary] = {}

        for s in statuses:
            if s.condition not in conditions:
                conditions[s.condition] = ConditionSummary(condition=s.condition)
            cs = conditions[s.condition]
            cs.total_docs += 1
            cs.total_pmids += s.pmids
            if s.readiness == "ready":
                cs.ready += 1
            elif s.readiness == "review_required":
                cs.review_required += 1
            else:
                cs.incomplete += 1

        return sorted(conditions.values(), key=lambda c: c.condition)

    def blockers(self) -> list[ReleaseBlocker]:
        """Get all release blockers across the platform."""
        blockers = []
        statuses = self._get_all_statuses()

        for s in statuses:
            if s.readiness == "incomplete":
                blockers.append(ReleaseBlocker(
                    condition=s.condition, doc_type=s.doc_type, tier=s.tier,
                    blocker_type="readiness_incomplete",
                    summary=f"{s.sections_failing} sections failed QA",
                ))
            if s.placeholders > 0:
                blockers.append(ReleaseBlocker(
                    condition=s.condition, doc_type=s.doc_type, tier=s.tier,
                    blocker_type="placeholder_content",
                    summary=f"{s.placeholders} placeholder sections",
                ))
            if s.readiness == "review_required":
                blockers.append(ReleaseBlocker(
                    condition=s.condition, doc_type=s.doc_type, tier=s.tier,
                    blocker_type="review_required",
                    summary=f"{s.sections_warning} sections have warnings",
                ))

        return blockers

    def release_ready(self, tier: str = "fellow") -> list[DocStatus]:
        """Get documents that are release-ready."""
        return [s for s in self._get_all_statuses() if s.readiness == "ready" and s.tier == tier]

    def pack_summary(self, condition: str, tier: str = "fellow") -> dict:
        """Get release pack summary for one condition/tier."""
        statuses = [
            s for s in self._get_all_statuses()
            if s.condition == condition and s.tier == tier
        ]
        ready = [s for s in statuses if s.readiness == "ready"]
        review = [s for s in statuses if s.readiness == "review_required"]
        incomplete = [s for s in statuses if s.readiness == "incomplete"]

        return {
            "condition": condition,
            "tier": tier,
            "total": len(statuses),
            "ready": len(ready),
            "review_required": len(review),
            "incomplete": len(incomplete),
            "release_ready": len(ready) == len(statuses),
            "ready_docs": [s.doc_type for s in ready],
            "blocked_docs": [
                {"doc_type": s.doc_type, "reason": s.readiness, "placeholders": s.placeholders}
                for s in review + incomplete
            ],
        }

    def _get_all_statuses(self) -> list[DocStatus]:
        """Compute operational status for all condition/blueprint/tier combinations."""
        if self._doc_statuses is not None:
            return self._doc_statuses

        from .assembler import CanonicalDocumentAssembler
        assembler = CanonicalDocumentAssembler(self.kb)

        statuses = []
        for cond in self.kb.list_conditions():
            for bp_slug in self.kb.list_blueprints():
                for tier in ["fellow", "partners"]:
                    bp = self.kb.get_blueprint(bp_slug)
                    if bp and tier not in bp.applicable_tiers:
                        continue
                    try:
                        _, prov = assembler.assemble(cond, bp_slug, tier)
                        statuses.append(DocStatus(
                            condition=cond,
                            doc_type=bp_slug,
                            tier=tier,
                            readiness=prov.readiness,
                            sections=prov.total_sections,
                            placeholders=prov.placeholder_sections,
                            pmids=prov.total_evidence_pmids,
                            sections_passing=prov.sections_passing,
                            sections_warning=prov.sections_warning,
                            sections_failing=prov.sections_failing,
                            has_provenance=True,
                        ))
                    except Exception:
                        statuses.append(DocStatus(
                            condition=cond, doc_type=bp_slug, tier=tier,
                            readiness="error",
                        ))

        self._doc_statuses = statuses
        return statuses


def _read_json_field(path: Path, field: str) -> str:
    """Read a single field from a JSON file."""
    try:
        data = json.loads(path.read_text())
        return data.get(field, "")
    except Exception:
        return ""
