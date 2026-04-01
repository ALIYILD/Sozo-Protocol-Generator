"""
Builds a concrete revision plan from structured instructions.

Takes RevisionInstruction objects (from CommentNormalizer) and maps them
against an existing DocumentSpec to produce an actionable RevisionPlan.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from ..schemas.documents import DocumentSpec, SectionContent
from .comment_normalizer import RevisionInstruction

logger = logging.getLogger(__name__)


@dataclass
class SectionEdit:
    """A concrete edit to apply to one section."""

    section_id: str = ""
    action: str = ""  # replace, append, shorten, expand, soften, strengthen, update, remove
    detail: str = ""
    parameters: dict = field(default_factory=dict)


@dataclass
class RevisionPlan:
    """Complete plan for revising a document."""

    document_id: str = ""
    condition_slug: str = ""
    instructions: list[RevisionInstruction] = field(default_factory=list)
    section_edits: dict[str, SectionEdit] = field(default_factory=dict)
    sections_to_remove: list[str] = field(default_factory=list)
    sections_to_add: list[dict] = field(default_factory=list)
    tone_adjustments: list[str] = field(default_factory=list)  # "soften" | "strengthen"
    modality_changes: list[dict] = field(default_factory=list)  # [{action, modality}]
    preserve_sections: list[str] = field(default_factory=list)
    evidence_updates: list[dict] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    summary: str = ""


class RevisionInstructionBuilder:
    """Converts a list of RevisionInstructions into a RevisionPlan."""

    def build_plan(
        self, spec: DocumentSpec, instructions: list[RevisionInstruction]
    ) -> RevisionPlan:
        """Build a revision plan from instructions against a DocumentSpec."""
        plan = RevisionPlan(
            document_id=spec.build_id or "",
            condition_slug=spec.condition_slug,
            instructions=list(instructions),
        )

        existing_section_ids = self._collect_section_ids(spec)
        logger.info(
            "Building plan for %d instructions against %d sections",
            len(instructions),
            len(existing_section_ids),
        )

        for inst in instructions:
            self._route_instruction(inst, plan, existing_section_ids)

        # Detect conflicts
        self._detect_conflicts(plan)

        n_edits = len(plan.section_edits)
        n_rm = len(plan.sections_to_remove)
        n_add = len(plan.sections_to_add)
        n_tone = len(plan.tone_adjustments)
        n_mod = len(plan.modality_changes)
        plan.summary = (
            f"Plan: {n_edits} section edit(s), {n_rm} removal(s), "
            f"{n_add} addition(s), {n_tone} tone change(s), {n_mod} modality change(s)"
        )
        if plan.conflicts:
            plan.summary += f"; {len(plan.conflicts)} conflict(s)"
        logger.info(plan.summary)
        return plan

    # ------------------------------------------------------------------
    # Routing
    # ------------------------------------------------------------------

    def _route_instruction(
        self,
        inst: RevisionInstruction,
        plan: RevisionPlan,
        existing_ids: set[str],
    ) -> None:
        """Route one instruction into the appropriate plan bucket."""
        target = inst.target
        action = inst.action

        # -- Modality changes --
        if target == "modality":
            plan.modality_changes.append(
                {
                    "action": action,
                    "modality": inst.parameters.get("modality", ""),
                }
            )
            return

        # -- Tone adjustments (global) --
        if target == "tone":
            plan.tone_adjustments.append(action)
            return

        # -- Evidence / references --
        if target == "evidence":
            plan.evidence_updates.append(
                {"action": action, "parameters": inst.parameters}
            )
            return

        # -- Section / table targeting --
        section_id = inst.section_id or self._parse_section_from_target(target)

        if action == "preserve" and section_id:
            plan.preserve_sections.append(section_id)
            return

        if action == "remove" and section_id:
            if section_id in existing_ids:
                plan.sections_to_remove.append(section_id)
            else:
                logger.warning(
                    "Cannot remove section '%s' — not found in spec", section_id
                )
            return

        if action == "add" and section_id and section_id not in existing_ids:
            plan.sections_to_add.append(
                {"section_id": section_id, "detail": inst.detail}
            )
            return

        # -- Section edits (soften, strengthen, shorten, expand, update, replace, append) --
        if section_id:
            if section_id not in existing_ids and action != "add":
                logger.warning(
                    "Section '%s' not in spec; creating add entry instead",
                    section_id,
                )
                plan.sections_to_add.append(
                    {"section_id": section_id, "detail": inst.detail}
                )
                return

            edit = SectionEdit(
                section_id=section_id,
                action=self._map_action_to_edit(action),
                detail=inst.detail,
                parameters=inst.parameters,
            )
            # If section already has an edit, merge or overwrite
            if section_id in plan.section_edits:
                existing = plan.section_edits[section_id]
                logger.info(
                    "Merging edit for section '%s': %s + %s",
                    section_id,
                    existing.action,
                    edit.action,
                )
                # Later instruction wins for action; combine details
                existing.detail = f"{existing.detail}; {edit.detail}"
                existing.action = edit.action
                existing.parameters.update(edit.parameters)
            else:
                plan.section_edits[section_id] = edit
            return

        # -- Tone adjustment scoped to a section --
        if action in ("soften", "strengthen") and section_id:
            plan.tone_adjustments.append(action)
            return

        # -- Document-level fallback --
        if target == "document":
            edit = SectionEdit(
                section_id="__document__",
                action=self._map_action_to_edit(action),
                detail=inst.detail,
                parameters=inst.parameters,
            )
            plan.section_edits["__document__"] = edit
            return

        logger.warning("Unhandled instruction: %s", inst)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _collect_section_ids(self, spec: DocumentSpec) -> set[str]:
        """Recursively collect all section IDs from a DocumentSpec."""
        ids: set[str] = set()
        for section in spec.sections:
            self._walk_sections(section, ids)
        return ids

    def _walk_sections(self, section: SectionContent, ids: set[str]) -> None:
        ids.add(section.section_id)
        for sub in section.subsections:
            self._walk_sections(sub, ids)

    def _parse_section_from_target(self, target: str) -> str:
        """Extract section id from 'section:foo' or 'table:foo' target strings."""
        if ":" in target:
            return target.split(":", 1)[1]
        return ""

    def _map_action_to_edit(self, action: str) -> str:
        """Normalize action verbs to edit actions."""
        mapping = {
            "replace": "replace",
            "add": "append",
            "update": "update",
            "shorten": "shorten",
            "expand": "expand",
            "soften": "soften",
            "strengthen": "strengthen",
            "reorder": "reorder",
        }
        return mapping.get(action, "update")

    def _detect_conflicts(self, plan: RevisionPlan) -> None:
        """Flag obvious conflicts in the plan."""
        # Section both removed and edited
        edited = set(plan.section_edits.keys())
        removed = set(plan.sections_to_remove)
        preserved = set(plan.preserve_sections)

        both_edited_and_removed = edited & removed
        for sid in both_edited_and_removed:
            plan.conflicts.append(
                f"Section '{sid}' is marked for both editing and removal"
            )

        both_preserved_and_removed = preserved & removed
        for sid in both_preserved_and_removed:
            plan.conflicts.append(
                f"Section '{sid}' is marked for both preservation and removal"
            )

        both_preserved_and_edited = preserved & edited
        for sid in both_preserved_and_edited:
            plan.conflicts.append(
                f"Section '{sid}' is marked for both preservation and editing"
            )

        # Contradictory tone
        tones = set(plan.tone_adjustments)
        if "soften" in tones and "strengthen" in tones:
            plan.conflicts.append(
                "Conflicting tone adjustments: both 'soften' and 'strengthen' requested"
            )
