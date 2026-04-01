"""
Applies revision plans to documents safely.

Takes a RevisionPlan (from RevisionInstructionBuilder) and applies it to a
DocumentSpec, producing a revised copy and a RevisionSummary.
"""
from __future__ import annotations

import copy
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from ..schemas.documents import DocumentSpec, SectionContent
from ..schemas.condition import ConditionSchema
from ..ai.revision_instruction_builder import RevisionPlan, SectionEdit

logger = logging.getLogger(__name__)

# Tone-replacement tables
_STRONG_TO_HEDGED: list[tuple[str, str]] = [
    ("demonstrates", "suggests"),
    ("demonstrates that", "suggests that"),
    ("proves", "suggests"),
    ("proven", "suggested"),
    ("clearly shows", "appears to show"),
    ("significant improvement", "potential improvement"),
    ("highly effective", "potentially effective"),
    ("effective", "potentially effective"),
    ("eliminates", "may reduce"),
    ("cures", "may alleviate"),
    ("guarantees", "may support"),
    ("definitive", "preliminary"),
    ("conclusive", "emerging"),
    ("dramatically", "notably"),
    ("all patients", "some patients"),
    ("always", "often"),
    ("never", "rarely"),
]

_HEDGED_TO_STRONG: list[tuple[str, str]] = [
    ("suggests", "demonstrates"),
    ("may", "is expected to"),
    ("potentially", ""),
    ("appears to", ""),
    ("preliminary", "established"),
    ("emerging", "robust"),
    ("some patients", "most patients"),
    ("might", "will likely"),
    ("could", "is likely to"),
]


@dataclass
class RevisionSummary:
    """Summary of changes applied during revision."""

    sections_modified: int = 0
    sections_removed: int = 0
    sections_added: int = 0
    sections_preserved: int = 0
    tone_changes: int = 0
    modality_changes: int = 0
    unresolved: list[str] = field(default_factory=list)
    diff_lines: list[str] = field(default_factory=list)  # human-readable diff


class RevisionEngine:
    """Applies structured revisions to a DocumentSpec."""

    def apply_revision(
        self,
        spec: DocumentSpec,
        plan: RevisionPlan,
        condition: ConditionSchema,
    ) -> tuple[DocumentSpec, RevisionSummary]:
        """Apply a revision plan, returning revised spec + summary."""
        revised = spec.model_copy(deep=True)
        summary = RevisionSummary()

        logger.info(
            "Applying revision plan: %s to %s", plan.summary, spec.condition_slug
        )

        # 1. Preserve sections (mark them so later steps skip them)
        preserved_ids = set(plan.preserve_sections)
        summary.sections_preserved = len(preserved_ids)

        # 2. Apply section edits
        for section_id, edit in plan.section_edits.items():
            if section_id in preserved_ids:
                logger.info("Skipping preserved section: %s", section_id)
                continue
            if section_id == "__document__":
                # Document-level edit: apply to all non-preserved sections
                for section in revised.sections:
                    if section.section_id not in preserved_ids:
                        original_content = section.content
                        section = self._apply_section_edit(section, edit)
                        if section.content != original_content:
                            summary.sections_modified += 1
                            summary.diff_lines.append(
                                f"~ {section.section_id}: {edit.action}"
                            )
                continue

            applied = self._apply_edit_to_sections(
                revised.sections, section_id, edit, preserved_ids
            )
            if applied:
                summary.sections_modified += 1
                summary.diff_lines.append(f"~ {section_id}: {edit.action}")
            else:
                summary.unresolved.append(
                    f"Could not apply edit to section '{section_id}'"
                )

        # 3. Apply tone adjustments
        for tone_action in plan.tone_adjustments:
            count = self._apply_tone_adjustment(revised, tone_action, preserved_ids)
            summary.tone_changes += count

        # 4. Apply modality changes
        for change in plan.modality_changes:
            changed = self._apply_modality_filter(revised, change)
            if changed:
                summary.modality_changes += 1
                summary.diff_lines.append(
                    f"M modality: {change['action']} {change['modality']}"
                )

        # 5. Remove sections
        for section_id in plan.sections_to_remove:
            if section_id in preserved_ids:
                logger.info("Skipping removal of preserved section: %s", section_id)
                continue
            removed = self._remove_section(revised, section_id)
            if removed:
                summary.sections_removed += 1
                summary.diff_lines.append(f"- {section_id}: removed")
            else:
                summary.unresolved.append(
                    f"Could not remove section '{section_id}'"
                )

        # 6. Add sections
        for entry in plan.sections_to_add:
            new_section = SectionContent(
                section_id=entry["section_id"],
                title=entry["section_id"].replace("_", " ").title(),
                content=entry.get("detail", ""),
                is_placeholder=True,
            )
            revised.sections.append(new_section)
            summary.sections_added += 1
            summary.diff_lines.append(f"+ {entry['section_id']}: added")

        # 7. Evidence updates (flag for manual review)
        for eu in plan.evidence_updates:
            revised.review_flags.append("EVIDENCE_UPDATE_REQUESTED")
            summary.diff_lines.append("! evidence: update requested")

        logger.info(
            "Revision complete: %d modified, %d removed, %d added, %d tone, %d modality",
            summary.sections_modified,
            summary.sections_removed,
            summary.sections_added,
            summary.tone_changes,
            summary.modality_changes,
        )
        return revised, summary

    # ------------------------------------------------------------------
    # Evidence-aware revision
    # ------------------------------------------------------------------

    def apply_evidence_revision(
        self,
        spec: DocumentSpec,
        condition: ConditionSchema,
        recency_years: int = 5,
        soften_weak: bool = True,
    ) -> tuple[DocumentSpec, RevisionSummary]:
        """Apply evidence-aware revisions: downgrade confidence on weak sections,
        soften language where evidence is limited, flag outdated sections.

        This NEVER fabricates evidence. It only adjusts tone and flags.
        """
        from ..evidence.section_evidence_mapper import SectionEvidenceMapper

        revised = spec.model_copy(deep=True)
        summary = RevisionSummary()
        mapper = SectionEvidenceMapper(recency_years=recency_years)

        # Build evidence items from condition
        items = mapper.build_evidence_items_from_condition(condition)
        profile = mapper.map_to_sections(revised, items)

        # Apply evidence metadata to spec
        revised = mapper.apply_evidence_to_spec(revised, profile)

        # Soften language in weak/unsupported sections
        if soften_weak:
            for section_id in profile.weak_sections + profile.unsupported_sections:
                for section in revised.sections:
                    if section.section_id == section_id:
                        original = section.content
                        section.content = self._soften_text(section.content)
                        if section.content != original:
                            summary.tone_changes += 1
                            summary.diff_lines.append(
                                f"~ {section_id}: softened (weak evidence)"
                            )

        # Flag outdated sections
        for section_id in profile.outdated_sections:
            for section in revised.sections:
                if section.section_id == section_id:
                    section.review_flags.append("EVIDENCE_OUTDATED")
                    summary.diff_lines.append(
                        f"! {section_id}: evidence may be outdated (>{recency_years} years)"
                    )

        # Flag conflicting sections
        for section_id in profile.conflicting_sections:
            for section in revised.sections:
                if section.section_id == section_id:
                    section.review_flags.append("EVIDENCE_CONFLICTING")
                    summary.diff_lines.append(
                        f"! {section_id}: conflicting evidence detected"
                    )

        summary.sections_modified = len(profile.weak_sections) + len(profile.outdated_sections)
        return revised, summary

    # ------------------------------------------------------------------
    # Section edits
    # ------------------------------------------------------------------

    def _apply_edit_to_sections(
        self,
        sections: list[SectionContent],
        target_id: str,
        edit: SectionEdit,
        preserved_ids: set[str],
    ) -> bool:
        """Walk sections to find and edit the target. Returns True if applied."""
        for i, section in enumerate(sections):
            if section.section_id == target_id:
                if section.section_id in preserved_ids:
                    return False
                sections[i] = self._apply_section_edit(section, edit)
                return True
            # Recurse into subsections
            if self._apply_edit_to_sections(
                section.subsections, target_id, edit, preserved_ids
            ):
                return True
        return False

    def _apply_section_edit(
        self, section: SectionContent, edit: SectionEdit
    ) -> SectionContent:
        """Apply a single edit to a section, returning the modified section."""
        action = edit.action

        if action == "soften":
            section.content = self._soften_text(section.content)
        elif action == "strengthen":
            section.content = self._strengthen_text(section.content)
        elif action == "shorten":
            section.content = self._shorten_text(section.content)
        elif action == "expand":
            # Cannot auto-expand; flag for manual review
            section.review_flags.append("EXPAND_REQUESTED")
            section.is_placeholder = True
        elif action == "replace":
            replacement = edit.parameters.get("content", "")
            if replacement:
                section.content = replacement
            else:
                section.review_flags.append("REPLACE_REQUESTED")
        elif action == "append":
            extra = edit.detail or ""
            if extra:
                section.content = section.content.rstrip() + "\n\n" + extra
        elif action == "update":
            # Generic update: flag for manual review with detail
            section.review_flags.append(f"UPDATE_REQUESTED: {edit.detail}")
        elif action == "reorder":
            section.review_flags.append("REORDER_REQUESTED")
        else:
            logger.warning("Unknown edit action: %s", action)

        return section

    # ------------------------------------------------------------------
    # Tone helpers
    # ------------------------------------------------------------------

    def _soften_text(self, text: str) -> str:
        """Replace strong language with hedged alternatives."""
        result = text
        for strong, hedged in _STRONG_TO_HEDGED:
            pattern = re.compile(re.escape(strong), re.IGNORECASE)
            result = pattern.sub(hedged, result)
        return result

    def _strengthen_text(self, text: str) -> str:
        """Replace hedged language with stronger alternatives."""
        result = text
        for hedged, strong in _HEDGED_TO_STRONG:
            if not strong:
                # Remove the hedging word entirely
                pattern = re.compile(re.escape(hedged) + r"\s*", re.IGNORECASE)
                result = pattern.sub("", result)
            else:
                pattern = re.compile(re.escape(hedged), re.IGNORECASE)
                result = pattern.sub(strong, result)
        return result

    def _shorten_text(self, text: str, max_sentences: int = 3) -> str:
        """Truncate content to the first N sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        if len(sentences) <= max_sentences:
            return text
        shortened = " ".join(sentences[:max_sentences])
        if not shortened.endswith((".", "!", "?")):
            shortened += "."
        return shortened

    # ------------------------------------------------------------------
    # Tone adjustment (global)
    # ------------------------------------------------------------------

    def _apply_tone_adjustment(
        self,
        spec: DocumentSpec,
        action: str,
        preserved_ids: set[str],
    ) -> int:
        """Apply tone adjustment to all non-preserved sections. Returns change count."""
        count = 0
        for section in spec.sections:
            count += self._tone_walk(section, action, preserved_ids)
        return count

    def _tone_walk(
        self,
        section: SectionContent,
        action: str,
        preserved_ids: set[str],
    ) -> int:
        """Recursively apply tone to a section tree."""
        count = 0
        if section.section_id not in preserved_ids and section.content:
            original = section.content
            if action == "soften":
                section.content = self._soften_text(section.content)
            elif action == "strengthen":
                section.content = self._strengthen_text(section.content)
            if section.content != original:
                count += 1
        for sub in section.subsections:
            count += self._tone_walk(sub, action, preserved_ids)
        return count

    # ------------------------------------------------------------------
    # Modality filtering
    # ------------------------------------------------------------------

    def _apply_modality_filter(
        self, spec: DocumentSpec, change: dict
    ) -> bool:
        """Apply a modality add/remove change. Returns True if spec was modified."""
        action = change.get("action", "")
        modality = change.get("modality", "").lower()
        if not modality:
            return False

        if action == "remove":
            return self._remove_modality_references(spec, modality)
        elif action == "add":
            # Adding a modality requires clinical data; flag for review
            spec.review_flags.append(f"ADD_MODALITY_REQUESTED: {modality}")
            return True
        return False

    def _remove_modality_references(
        self, spec: DocumentSpec, modality: str
    ) -> bool:
        """Remove references to a modality from section content and tables."""
        changed = False

        for section in spec.sections:
            if self._strip_modality_from_section(section, modality):
                changed = True

        # Filter protocol tables in section tables
        for section in spec.sections:
            original_table_count = len(section.tables)
            section.tables = [
                t
                for t in section.tables
                if not self._table_matches_modality(t, modality)
            ]
            if len(section.tables) != original_table_count:
                changed = True

        return changed

    def _strip_modality_from_section(
        self, section: SectionContent, modality: str
    ) -> bool:
        """Remove modality mentions from section content."""
        changed = False
        if modality.lower() in section.content.lower():
            # Remove lines that mention the modality
            lines = section.content.split("\n")
            filtered = [
                line
                for line in lines
                if modality.lower() not in line.lower()
            ]
            new_content = "\n".join(filtered)
            if new_content != section.content:
                section.content = new_content
                changed = True

        for sub in section.subsections:
            if self._strip_modality_from_section(sub, modality):
                changed = True

        return changed

    def _table_matches_modality(self, table: dict, modality: str) -> bool:
        """Check if a table dict is associated with a specific modality."""
        # Check common keys
        for key in ("modality", "type", "name", "label"):
            val = table.get(key, "")
            if isinstance(val, str) and modality.lower() in val.lower():
                return True
        return False

    # ------------------------------------------------------------------
    # Section removal
    # ------------------------------------------------------------------

    def _remove_section(self, spec: DocumentSpec, section_id: str) -> bool:
        """Remove a section by ID. Returns True if found and removed."""
        for i, section in enumerate(spec.sections):
            if section.section_id == section_id:
                spec.sections.pop(i)
                return True
            if self._remove_subsection(section, section_id):
                return True
        return False

    def _remove_subsection(
        self, parent: SectionContent, section_id: str
    ) -> bool:
        """Remove a subsection by ID from a parent section."""
        for i, sub in enumerate(parent.subsections):
            if sub.section_id == section_id:
                parent.subsections.pop(i)
                return True
            if self._remove_subsection(sub, section_id):
                return True
        return False
