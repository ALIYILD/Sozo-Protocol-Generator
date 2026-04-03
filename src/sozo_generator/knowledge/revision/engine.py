"""
Review-Driven Regeneration Engine.

Builds change plans from parsed comments, applies safe changes,
regenerates through the canonical path, and produces diffs + history.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from .models import (
    ChangePlan,
    ChangeRequest,
    ChangeStatus,
    ChangeTarget,
    RegenerationResult,
    ReviewCommentSet,
)
from .parser import classify_all, comments_to_change_requests

logger = logging.getLogger(__name__)


class RevisionEngine:
    """Orchestrates review-driven regeneration through the canonical path.

    Usage:
        engine = RevisionEngine()

        # Full pipeline
        result = engine.review_and_regenerate(
            document_id="canon-abc123",
            condition="parkinsons",
            blueprint="evidence_based_protocol",
            tier="fellow",
            comments=comment_set,
        )

        # Or step by step
        plan = engine.create_change_plan(comment_set)
        result = engine.execute_plan(plan)
    """

    def __init__(self, output_dir: str | Path | None = None):
        self.output_dir = Path(output_dir) if output_dir else Path("outputs")
        self._history_dir = self.output_dir / "revision_history"
        self._history_dir.mkdir(parents=True, exist_ok=True)

    def create_change_plan(
        self,
        comments: ReviewCommentSet,
        dry_run: bool = True,
    ) -> ChangePlan:
        """Parse comments and create an inspectable change plan.

        Args:
            comments: Set of reviewer comments
            dry_run: If True, plan is created but not applied

        Returns:
            ChangePlan with mapped changes, impacts, and safety flags
        """
        # 1. Classify comments
        classify_all(comments)

        # 2. Convert to change requests
        requests = comments_to_change_requests(comments)

        # 3. Build plan
        plan = ChangePlan(
            document_id=comments.document_id,
            condition_slug=comments.condition_slug,
            blueprint_slug=comments.blueprint_slug,
            tier=comments.tier,
        )

        # Separate applicable from blocked
        for cr in requests:
            if cr.status == ChangeStatus.BLOCKED:
                plan.blocked_changes.append(cr)
            else:
                plan.changes.append(cr)

        # Compute impact
        plan.impacted_sections = list(set(
            cr.target_section for cr in plan.changes if cr.target_section
        ))

        plan.requires_evidence_review = any(cr.evidence_sensitive for cr in plan.changes)
        plan.requires_clinical_review = any(
            cr.target_type in (ChangeTarget.KNOWLEDGE_PATCH, ChangeTarget.SHARED_RULE_PATCH)
            for cr in plan.changes
        )
        plan.safe_to_auto_apply = (
            not plan.requires_evidence_review
            and not plan.requires_clinical_review
            and all(not cr.requires_manual_approval for cr in plan.changes)
            and plan.blocked_count == 0
        )

        # Add warnings
        if plan.requires_evidence_review:
            plan.warnings.append("Plan includes evidence-sensitive changes — manual review recommended")
        if plan.requires_clinical_review:
            plan.warnings.append("Plan includes knowledge/rule patches — clinical review required")
        if plan.blocked_count > 0:
            plan.warnings.append(f"{plan.blocked_count} changes were blocked as unsafe")

        return plan

    def execute_plan(
        self,
        plan: ChangePlan,
        force: bool = False,
    ) -> RegenerationResult:
        """Execute a change plan by regenerating through the canonical path.

        Section overrides are applied as content patches on top of
        the canonical assembly. Blueprint/knowledge patches are logged
        as suggestions but not auto-applied to source files.

        Args:
            plan: The change plan to execute
            force: If True, execute even if plan has manual approval requirements
        """
        result = RegenerationResult(
            plan_id=plan.plan_id,
            old_document_id=plan.document_id,
            condition_slug=plan.condition_slug,
            blueprint_slug=plan.blueprint_slug,
            tier=plan.tier,
        )

        if not force and not plan.safe_to_auto_apply:
            if plan.requires_evidence_review or plan.requires_clinical_review:
                result.error = "Plan requires manual review — use force=True to override"
                result.warnings = plan.warnings
                return result

        try:
            # Load knowledge base and assemble
            from ..base import KnowledgeBase
            from ..assembler import CanonicalDocumentAssembler

            kb = KnowledgeBase()
            kb.load_all()

            assembler = CanonicalDocumentAssembler(kb)
            spec, provenance_before = assembler.assemble(
                plan.condition_slug, plan.blueprint_slug, plan.tier
            )

            result.readiness_before = provenance_before.readiness
            result.pmids_before = provenance_before.total_evidence_pmids

            # Apply section overrides to the spec
            applied = []
            for cr in plan.applicable_changes:
                if cr.target_type == ChangeTarget.SECTION_OVERRIDE and cr.target_section:
                    # Apply as section content addition/note
                    for section in spec.sections:
                        if section.section_id == cr.target_section:
                            # Add review note to content
                            note = f"\n[REVIEWER NOTE: {cr.requested_action}] {cr.proposed_resolution}"
                            section.content = (section.content or "") + note
                            section.review_flags.append(
                                f"Review change applied: {cr.requested_action} ({cr.change_id})"
                            )
                            applied.append(cr.change_id)
                            result.sections_changed.append(cr.target_section)
                            cr.status = ChangeStatus.APPLIED
                            break
                    else:
                        cr.status = ChangeStatus.DEFERRED
                        result.warnings.append(f"Section '{cr.target_section}' not found — change deferred")
                elif cr.target_type in (ChangeTarget.KNOWLEDGE_PATCH, ChangeTarget.SHARED_RULE_PATCH):
                    # Log as suggestion, don't auto-modify source
                    cr.status = ChangeStatus.DEFERRED
                    result.warnings.append(
                        f"Knowledge/rule patch suggested for {cr.target_section}: {cr.proposed_resolution}"
                    )
                elif cr.target_type == ChangeTarget.BLUEPRINT_PATCH:
                    cr.status = ChangeStatus.DEFERRED
                    result.warnings.append(
                        f"Blueprint patch suggested: {cr.proposed_resolution}"
                    )
                else:
                    applied.append(cr.change_id)
                    cr.status = ChangeStatus.APPLIED

            result.applied_changes = applied
            result.blocked_changes = [cr.change_id for cr in plan.blocked_changes]

            # Render the modified spec
            from ...generation.service import GenerationService
            svc = GenerationService(with_visuals=False, with_qa=False)
            output_path = svc.exporter.renderer.render(spec)
            result.output_path = str(output_path)

            # Get new provenance
            _, provenance_after = assembler.assemble(
                plan.condition_slug, plan.blueprint_slug, plan.tier
            )
            result.readiness_after = provenance_after.readiness
            result.pmids_after = provenance_after.total_evidence_pmids
            result.new_document_id = f"rev-{result.result_id}"

            # Save provenance sidecar
            prov_path = Path(output_path).with_suffix(".provenance.json")
            prov_data = provenance_after.to_dict()
            prov_data["revision"] = {
                "plan_id": plan.plan_id,
                "parent_document_id": plan.document_id,
                "applied_changes": result.applied_changes,
                "sections_changed": result.sections_changed,
            }
            prov_path.write_text(json.dumps(prov_data, indent=2))
            result.provenance_path = str(prov_path)

            # Finalize and save revision history
            result.success = True
            self._save_history(plan, result)

            logger.info(
                f"Regeneration complete: {len(applied)} changes applied, "
                f"{len(result.blocked_changes)} blocked, "
                f"readiness: {result.readiness_before} → {result.readiness_after}"
            )

        except Exception as e:
            result.error = str(e)
            logger.error(f"Regeneration failed: {e}", exc_info=True)

        return result

    def review_and_regenerate(
        self,
        document_id: str,
        condition: str,
        blueprint: str,
        tier: str,
        comments: ReviewCommentSet,
        force: bool = False,
    ) -> RegenerationResult:
        """Full pipeline: parse comments → plan → regenerate.

        This is the main entry point for review-driven regeneration.
        """
        # Set document metadata on comment set
        comments.document_id = document_id
        comments.condition_slug = condition
        comments.blueprint_slug = blueprint
        comments.tier = tier

        # Create plan
        plan = self.create_change_plan(comments)

        # Execute
        return self.execute_plan(plan, force=force)

    def _save_history(self, plan: ChangePlan, result: RegenerationResult):
        """Save revision history for auditability."""
        history_path = self._history_dir / f"{result.result_id}.json"
        history = {
            "result_id": result.result_id,
            "plan_id": plan.plan_id,
            "old_document_id": result.old_document_id,
            "new_document_id": result.new_document_id,
            "condition": result.condition_slug,
            "blueprint": result.blueprint_slug,
            "tier": result.tier,
            "created_at": result.created_at,
            "applied_changes": result.applied_changes,
            "blocked_changes": result.blocked_changes,
            "sections_changed": result.sections_changed,
            "readiness_before": result.readiness_before,
            "readiness_after": result.readiness_after,
            "success": result.success,
            "error": result.error,
            "plan_summary": plan.to_text(),
            "result_summary": result.to_text(),
        }
        history_path.write_text(json.dumps(history, indent=2))
        result.review_record_path = str(history_path)
