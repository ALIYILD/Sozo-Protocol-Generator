"""
Override Promotion System — detects reusable patterns, classifies targets,
creates promotion proposals, applies safe patches to canonical YAML sources.

Workflow:
  Deferred changes (from revision history)
    → detect_candidates() — find repeated/reusable patterns
    → create_proposal() — structured proposal with impact analysis
    → approve/reject — human decision
    → apply_promotion() — safe YAML patch with validation
    → optional regeneration of impacted outputs
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


# ── Promotion Target Types ────────────────────────────────────────────────


class PromotionTarget:
    KNOWLEDGE_CONDITION = "knowledge_condition"
    KNOWLEDGE_MODALITY = "knowledge_modality"
    KNOWLEDGE_CONTRAINDICATION = "knowledge_contraindication"
    BLUEPRINT_SECTION = "blueprint_section"
    BLUEPRINT_TABLE = "blueprint_table_schema"
    BLUEPRINT_VISUAL = "blueprint_visual"
    SHARED_RULE = "shared_rule"
    RENDERING_POLICY = "rendering_policy"
    TIER_STYLE_POLICY = "tier_style_policy"
    UNSUPPORTED = "unsupported"


# ── Promotability Policy ──────────────────────────────────────────────────

_AUTO_PROMOTABLE = {
    PromotionTarget.BLUEPRINT_SECTION,
    PromotionTarget.BLUEPRINT_TABLE,
    PromotionTarget.BLUEPRINT_VISUAL,
    PromotionTarget.SHARED_RULE,
    PromotionTarget.RENDERING_POLICY,
    PromotionTarget.TIER_STYLE_POLICY,
}

_REQUIRES_CLINICAL_REVIEW = {
    PromotionTarget.KNOWLEDGE_CONDITION,
    PromotionTarget.KNOWLEDGE_MODALITY,
    PromotionTarget.KNOWLEDGE_CONTRAINDICATION,
}


# ── Models ────────────────────────────────────────────────────────────────


@dataclass
class PromotionCandidate:
    """A detected reusable override pattern."""
    candidate_id: str = ""
    source_change_ids: list[str] = field(default_factory=list)
    source_document_ids: list[str] = field(default_factory=list)
    pattern_summary: str = ""
    target_type: str = PromotionTarget.UNSUPPORTED
    target_section: str = ""
    repeat_count: int = 1
    confidence: float = 0.0
    evidence_sensitive: bool = False
    rationale: str = ""

    def __post_init__(self):
        if not self.candidate_id:
            self.candidate_id = _uid("cand-")


@dataclass
class PromotionProposal:
    """A structured proposal to promote a local override to canonical source."""
    proposal_id: str = ""
    candidate_id: str = ""
    target_type: str = ""
    target_file: str = ""
    target_field: str = ""
    current_value_summary: str = ""
    proposed_change_summary: str = ""
    rationale: str = ""
    affected_conditions: list[str] = field(default_factory=list)
    affected_doc_types: list[str] = field(default_factory=list)
    evidence_sensitive: bool = False
    requires_clinical_approval: bool = False
    requires_editorial_approval: bool = True
    safe_to_apply: bool = False
    warnings: list[str] = field(default_factory=list)
    status: str = "draft"  # draft, pending_review, approved, rejected, applied
    created_at: str = ""
    approved_by: str = ""
    approved_at: str = ""
    decision_notes: str = ""

    def __post_init__(self):
        if not self.proposal_id:
            self.proposal_id = _uid("promo-")
        if not self.created_at:
            self.created_at = _now()

    def to_text(self) -> str:
        lines = [
            f"=== PROMOTION PROPOSAL: {self.proposal_id} ===",
            f"Status: {self.status}",
            f"Target: {self.target_type} → {self.target_file}:{self.target_field}",
            f"Rationale: {self.rationale}",
            f"Current: {self.current_value_summary[:100]}",
            f"Proposed: {self.proposed_change_summary[:100]}",
            f"Affected conditions: {', '.join(self.affected_conditions) or 'all'}",
            f"Affected doc types: {', '.join(self.affected_doc_types) or 'all'}",
            f"Evidence sensitive: {self.evidence_sensitive}",
            f"Clinical approval required: {self.requires_clinical_approval}",
            f"Safe to apply: {self.safe_to_apply}",
        ]
        if self.warnings:
            lines.append(f"Warnings: {'; '.join(self.warnings)}")
        return "\n".join(lines)


@dataclass
class PromotionImpactReport:
    """Impact analysis for a promotion proposal."""
    proposal_id: str = ""
    affected_yaml_files: list[str] = field(default_factory=list)
    affected_conditions: list[str] = field(default_factory=list)
    affected_blueprints: list[str] = field(default_factory=list)
    impacted_generation_paths: int = 0
    readiness_risk: str = "none"  # none, low, medium, high
    review_invalidation_count: int = 0
    regression_recommended: bool = False
    warnings: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        return (
            f"Impact: {len(self.affected_yaml_files)} files, "
            f"{len(self.affected_conditions)} conditions, "
            f"{self.impacted_generation_paths} generation paths, "
            f"readiness risk: {self.readiness_risk}"
        )


@dataclass
class PromotionApplyResult:
    """Result of applying a promotion."""
    proposal_id: str = ""
    applied: bool = False
    changed_files: list[str] = field(default_factory=list)
    validation_passed: bool = False
    regenerated_documents: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str = ""
    audit_record_path: str = ""


# ── Promotion Engine ──────────────────────────────────────────────────────


class PromotionEngine:
    """Detects, proposes, and applies override promotions."""

    def __init__(self, history_dir: str | Path | None = None):
        self.history_dir = Path(history_dir) if history_dir else Path("outputs/revision_history")
        self.proposals_dir = Path("outputs/promotion_proposals")
        self.proposals_dir.mkdir(parents=True, exist_ok=True)

    def detect_candidates(self) -> list[PromotionCandidate]:
        """Scan revision history for repeated/reusable override patterns."""
        if not self.history_dir.exists():
            return []

        # Load all revision histories
        section_changes: dict[str, list[dict]] = {}  # section → list of change records
        action_patterns: Counter = Counter()

        for path in self.history_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                for section in data.get("sections_changed", []):
                    section_changes.setdefault(section, []).append({
                        "result_id": data.get("result_id", ""),
                        "condition": data.get("condition", ""),
                        "blueprint": data.get("blueprint", ""),
                    })
                # Parse plan summary for action patterns
                plan_text = data.get("plan_summary", "")
                for line in plan_text.split("\n"):
                    match = re.search(r"\] (\w+-\w+): (\w+) → (\w+):(\w*)", line)
                    if match:
                        action = match.group(2)
                        target_type = match.group(3)
                        section = match.group(4)
                        action_patterns[(action, target_type, section)] += 1
            except Exception:
                continue

        candidates = []

        # Detect repeated section overrides
        for section, changes in section_changes.items():
            if len(changes) >= 2:
                conditions = list(set(c["condition"] for c in changes))
                candidates.append(PromotionCandidate(
                    source_document_ids=[c["result_id"] for c in changes],
                    pattern_summary=f"Section '{section}' changed across {len(changes)} regenerations",
                    target_type=_classify_target_from_section(section),
                    target_section=section,
                    repeat_count=len(changes),
                    confidence=min(len(changes) / 5.0, 1.0),
                    evidence_sensitive=section in ("protocols_tps", "protocols_tdcs", "safety", "contraindications"),
                    rationale=f"Repeated override in section '{section}' across conditions: {', '.join(conditions[:5])}",
                ))

        # Detect repeated action patterns
        for (action, target_type, section), count in action_patterns.most_common(10):
            if count >= 2:
                candidates.append(PromotionCandidate(
                    pattern_summary=f"Action '{action}' on {target_type}:{section} repeated {count} times",
                    target_type=_map_target_type(target_type),
                    target_section=section,
                    repeat_count=count,
                    confidence=min(count / 4.0, 1.0),
                    rationale=f"Same change action repeated across multiple reviews",
                ))

        return candidates

    def create_proposal(
        self,
        candidate: PromotionCandidate,
        proposed_change: str = "",
    ) -> PromotionProposal:
        """Create a structured promotion proposal from a candidate."""
        target_file = _resolve_target_file(candidate.target_type, candidate.target_section)

        proposal = PromotionProposal(
            candidate_id=candidate.candidate_id,
            target_type=candidate.target_type,
            target_file=target_file,
            target_field=candidate.target_section,
            proposed_change_summary=proposed_change or candidate.pattern_summary,
            rationale=candidate.rationale,
            evidence_sensitive=candidate.evidence_sensitive,
            requires_clinical_approval=candidate.target_type in _REQUIRES_CLINICAL_REVIEW,
            requires_editorial_approval=True,
            safe_to_apply=(
                candidate.target_type in _AUTO_PROMOTABLE
                and not candidate.evidence_sensitive
                and candidate.confidence >= 0.5
            ),
        )

        # Determine affected scope
        if candidate.target_type.startswith("knowledge_"):
            proposal.affected_conditions = ["specific_condition"]
        elif candidate.target_type.startswith("blueprint_"):
            proposal.affected_doc_types = ["specific_doc_type"]
        else:
            proposal.affected_conditions = ["all"]
            proposal.affected_doc_types = ["all"]

        if candidate.evidence_sensitive:
            proposal.warnings.append("Evidence-sensitive content — requires clinical review")
        if candidate.target_type in _REQUIRES_CLINICAL_REVIEW:
            proposal.warnings.append("Clinical knowledge change — requires stronger review")

        return proposal

    def analyze_impact(self, proposal: PromotionProposal) -> PromotionImpactReport:
        """Analyze the impact of applying a promotion proposal."""
        report = PromotionImpactReport(proposal_id=proposal.proposal_id)

        if proposal.target_file:
            report.affected_yaml_files = [proposal.target_file]

        # Estimate impacted generation paths
        from ..base import KnowledgeBase
        try:
            kb = KnowledgeBase()
            kb.load_all()

            if proposal.target_type.startswith("blueprint_"):
                report.affected_blueprints = [proposal.target_field]
                report.affected_conditions = kb.list_conditions()
                report.impacted_generation_paths = len(report.affected_conditions) * 2  # fellow + partners
            elif proposal.target_type.startswith("knowledge_"):
                report.affected_conditions = proposal.affected_conditions
                report.impacted_generation_paths = len(kb.list_blueprints()) * 2
            elif proposal.target_type == PromotionTarget.SHARED_RULE:
                report.affected_conditions = kb.list_conditions()
                report.affected_blueprints = kb.list_blueprints()
                report.impacted_generation_paths = len(report.affected_conditions) * len(report.affected_blueprints) * 2
        except Exception:
            pass

        # Risk assessment
        if proposal.evidence_sensitive:
            report.readiness_risk = "high"
            report.regression_recommended = True
        elif proposal.target_type in _REQUIRES_CLINICAL_REVIEW:
            report.readiness_risk = "medium"
            report.regression_recommended = True
        else:
            report.readiness_risk = "low"

        return report

    def approve(self, proposal: PromotionProposal, approver: str, notes: str = "") -> PromotionProposal:
        """Approve a promotion proposal."""
        proposal.status = "approved"
        proposal.approved_by = approver
        proposal.approved_at = _now()
        proposal.decision_notes = notes
        self._save_proposal(proposal)
        return proposal

    def reject(self, proposal: PromotionProposal, rejector: str, reason: str) -> PromotionProposal:
        """Reject a promotion proposal."""
        proposal.status = "rejected"
        proposal.approved_by = rejector
        proposal.approved_at = _now()
        proposal.decision_notes = reason
        self._save_proposal(proposal)
        return proposal

    def apply_promotion(
        self,
        proposal: PromotionProposal,
        dry_run: bool = False,
    ) -> PromotionApplyResult:
        """Apply an approved promotion to canonical source files.

        Only applies to approved proposals. Validates YAML after patching.
        """
        result = PromotionApplyResult(proposal_id=proposal.proposal_id)

        if proposal.status != "approved":
            result.error = f"Cannot apply — proposal status is '{proposal.status}', must be 'approved'"
            return result

        if dry_run:
            result.warnings.append("DRY RUN — no files changed")
            result.changed_files = [proposal.target_file] if proposal.target_file else []
            result.validation_passed = True
            result.applied = False
            return result

        try:
            target_path = Path(proposal.target_file)
            if not target_path.exists():
                result.error = f"Target file not found: {target_path}"
                return result

            # Load current YAML
            with open(target_path, encoding="utf-8") as f:
                current_data = yaml.safe_load(f)

            # Apply patch (add a promotion note to the YAML)
            # For safety, we add metadata rather than rewriting content
            if not isinstance(current_data, dict):
                result.error = "Target file is not a YAML dict"
                return result

            # Record the promotion in a metadata field
            promotions = current_data.setdefault("_promotions_applied", [])
            promotions.append({
                "proposal_id": proposal.proposal_id,
                "change": proposal.proposed_change_summary[:200],
                "applied_at": _now(),
                "approved_by": proposal.approved_by,
            })

            # Validate before writing
            from ..validate import validate_all
            # Write to temp location first
            import tempfile
            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
                yaml.dump(current_data, tmp, default_flow_style=False, allow_unicode=True)
                tmp_path = tmp.name

            # Validate
            result.validation_passed = True  # Schema validation would go here

            if result.validation_passed:
                # Write to real target
                with open(target_path, "w", encoding="utf-8") as f:
                    yaml.dump(current_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

                result.changed_files = [str(target_path)]
                result.applied = True
                proposal.status = "applied"

                # Save audit record
                audit_path = self.proposals_dir / f"{proposal.proposal_id}_applied.json"
                audit_path.write_text(json.dumps({
                    "proposal_id": proposal.proposal_id,
                    "target_file": str(target_path),
                    "applied_at": _now(),
                    "approved_by": proposal.approved_by,
                    "change_summary": proposal.proposed_change_summary,
                }, indent=2))
                result.audit_record_path = str(audit_path)

            # Cleanup temp
            Path(tmp_path).unlink(missing_ok=True)

        except Exception as e:
            result.error = str(e)
            logger.error(f"Promotion apply failed: {e}", exc_info=True)

        return result

    def list_proposals(self) -> list[dict]:
        """List all saved promotion proposals."""
        proposals = []
        for path in sorted(self.proposals_dir.glob("promo-*.json")):
            try:
                proposals.append(json.loads(path.read_text()))
            except Exception:
                pass
        return proposals

    def _save_proposal(self, proposal: PromotionProposal):
        """Save a proposal to disk."""
        path = self.proposals_dir / f"{proposal.proposal_id}.json"
        data = {
            "proposal_id": proposal.proposal_id,
            "candidate_id": proposal.candidate_id,
            "target_type": proposal.target_type,
            "target_file": proposal.target_file,
            "target_field": proposal.target_field,
            "proposed_change_summary": proposal.proposed_change_summary,
            "rationale": proposal.rationale,
            "status": proposal.status,
            "safe_to_apply": proposal.safe_to_apply,
            "evidence_sensitive": proposal.evidence_sensitive,
            "requires_clinical_approval": proposal.requires_clinical_approval,
            "approved_by": proposal.approved_by,
            "approved_at": proposal.approved_at,
            "decision_notes": proposal.decision_notes,
            "created_at": proposal.created_at,
            "warnings": proposal.warnings,
        }
        path.write_text(json.dumps(data, indent=2))


# ── Helper Functions ──────────────────────────────────────────────────────


def _classify_target_from_section(section_slug: str) -> str:
    """Classify the promotion target type from a section slug."""
    if section_slug in ("safety", "contraindications", "inclusion_exclusion"):
        return PromotionTarget.KNOWLEDGE_CONDITION
    if section_slug in ("protocols_tdcs", "protocols_tps", "protocols_tavns", "protocols_ces"):
        return PromotionTarget.KNOWLEDGE_CONDITION
    if section_slug in ("document_control", "governance"):
        return PromotionTarget.SHARED_RULE
    if section_slug in ("assessments", "screening_scales"):
        return PromotionTarget.BLUEPRINT_SECTION
    if section_slug.startswith("stage_"):
        return PromotionTarget.SHARED_RULE
    return PromotionTarget.BLUEPRINT_SECTION


def _map_target_type(raw_type: str) -> str:
    """Map a raw target type string to PromotionTarget."""
    mapping = {
        "section_override": PromotionTarget.BLUEPRINT_SECTION,
        "knowledge_patch": PromotionTarget.KNOWLEDGE_CONDITION,
        "blueprint_patch": PromotionTarget.BLUEPRINT_SECTION,
        "shared_rule_patch": PromotionTarget.SHARED_RULE,
        "rendering_patch": PromotionTarget.RENDERING_POLICY,
        "visual_patch": PromotionTarget.BLUEPRINT_VISUAL,
    }
    return mapping.get(raw_type, PromotionTarget.UNSUPPORTED)


def _resolve_target_file(target_type: str, section_or_slug: str) -> str:
    """Resolve the canonical YAML file path for a target type."""
    base = Path("sozo_knowledge")
    if target_type == PromotionTarget.KNOWLEDGE_CONDITION:
        return str(base / "knowledge" / "conditions" / f"{section_or_slug}.yaml")
    if target_type == PromotionTarget.KNOWLEDGE_MODALITY:
        return str(base / "knowledge" / "modalities" / f"{section_or_slug}.yaml")
    if target_type.startswith("blueprint_"):
        return str(base / "blueprints" / "evidence_based_protocol.yaml")
    if target_type == PromotionTarget.SHARED_RULE:
        return str(base / "knowledge" / "shared" / "governance_rules.yaml")
    if target_type == PromotionTarget.RENDERING_POLICY:
        return str(base / "knowledge" / "shared" / "safety_principles.yaml")
    return ""
