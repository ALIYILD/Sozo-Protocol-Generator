"""
Doctor comment normalizer — converts free-text clinical feedback into
structured revision instructions.

SAFETY: This module interprets doctor intent. It never generates clinical
content. Revisions come from ConditionSchema verified data.
"""
from __future__ import annotations

import re
import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class RevisionInstruction:
    """A single structured revision instruction."""

    instruction_id: str = ""
    target: str = ""  # "document", "section:{id}", "table:{id}", "tone", "evidence", "modality"
    action: str = ""  # "replace", "add", "remove", "update", "strengthen", "soften", "reorder", "preserve"
    section_id: Optional[str] = None
    detail: str = ""  # human-readable description
    parameters: dict = field(default_factory=dict)  # action-specific params
    priority: str = "normal"  # "high", "normal", "low"
    source_comment: str = ""


@dataclass
class NormalizedComments:
    """Result of normalizing doctor comments."""

    instructions: list[RevisionInstruction] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)  # comments that couldn't be parsed
    summary: str = ""


# ---------------------------------------------------------------------------
# Pattern tables
# ---------------------------------------------------------------------------

# Maps keyword tokens to canonical action verbs
_ACTION_KEYWORDS: dict[str, str] = {
    "remove": "remove",
    "delete": "remove",
    "drop": "remove",
    "cut": "remove",
    "add": "add",
    "include": "add",
    "insert": "add",
    "update": "update",
    "change": "update",
    "revise": "update",
    "needs": "update",
    "replace": "replace",
    "swap": "replace",
    "strengthen": "strengthen",
    "stronger": "strengthen",
    "more assertive": "strengthen",
    "soften": "soften",
    "tone down": "soften",
    "more conservative": "soften",
    "cautious": "soften",
    "keep": "preserve",
    "preserve": "preserve",
    "exactly as is": "preserve",
    "don't change": "preserve",
    "do not change": "preserve",
    "shorten": "shorten",
    "shorter": "shorten",
    "make shorter": "shorten",
    "make the overview shorter": "shorten",
    "trim": "shorten",
    "condense": "shorten",
    "expand": "expand",
    "longer": "expand",
    "elaborate": "expand",
    "more detail": "expand",
    "reorder": "reorder",
    "rearrange": "reorder",
    "move": "reorder",
}

# Known modality tokens (case-insensitive matching)
_MODALITY_TOKENS: dict[str, str] = {
    "tps": "tps",
    "tdcs": "tdcs",
    "tavns": "tavns",
    "ces": "ces",
    "multimodal": "multimodal",
}

# Section-name aliases mapped to canonical section ids
_SECTION_ALIASES: dict[str, str] = {
    "overview": "overview",
    "introduction": "overview",
    "intro": "overview",
    "safety": "safety",
    "safety section": "safety",
    "protocol": "protocols",
    "protocols": "protocols",
    "protocol table": "protocols",
    "treatment": "protocols",
    "exclusion": "exclusion",
    "exclusion criteria": "exclusion",
    "inclusion": "inclusion",
    "inclusion criteria": "inclusion",
    "reference": "references",
    "references": "references",
    "evidence": "evidence",
    "phenotype": "phenotypes",
    "phenotypes": "phenotypes",
    "phenotype table": "phenotypes",
    "assessment": "assessment",
    "network": "networks",
    "networks": "networks",
    "pathophysiology": "pathophysiology",
    "symptoms": "symptoms",
    "contraindications": "contraindications",
}

# Tone-related phrases
_TONE_PHRASES: list[tuple[str, str]] = [
    ("more conservative", "soften"),
    ("stronger language", "strengthen"),
    ("cautious", "soften"),
    ("tone down", "soften"),
    ("less assertive", "soften"),
    ("more assertive", "strengthen"),
    ("hedged", "soften"),
    ("bolder", "strengthen"),
]

# Evidence-related phrases
_EVIDENCE_PHRASES: list[str] = [
    "more recent evidence",
    "update references",
    "newer studies",
    "latest research",
    "update the references",
    "latest studies",
    "recent literature",
    "last 3 years",
    "last 5 years",
    "last three years",
    "last five years",
    "recent publications",
    "up to date evidence",
    "up-to-date",
    "current evidence",
    "remove weakly supported",
    "remove weak claims",
    "conservative wording",
    "conservative language",
    "cautious wording",
    "cautious language",
    "evidence is limited",
    "limited evidence",
    "hedge where",
    "downgrade confidence",
    "recent literature",
    "newer evidence",
]


class CommentNormalizer:
    """Parses doctor free-text into RevisionInstruction objects."""

    def normalize(
        self, comments: list[str], section_ids: list[str] | None = None
    ) -> NormalizedComments:
        """Parse multiple comments into instructions."""
        result = NormalizedComments()
        for comment in comments:
            instructions = self.normalize_single(comment, section_ids)
            if instructions:
                result.instructions.extend(instructions)
            else:
                result.unresolved.append(comment)
                logger.warning("Could not parse comment: %s", comment)

        n_inst = len(result.instructions)
        n_unresolved = len(result.unresolved)
        result.summary = (
            f"Parsed {n_inst} instruction(s) from {len(comments)} comment(s)"
            + (f"; {n_unresolved} unresolved" if n_unresolved else "")
        )
        logger.info(result.summary)
        return result

    def normalize_single(
        self, comment: str, section_ids: list[str] | None = None
    ) -> list[RevisionInstruction]:
        """Parse one comment into zero or more RevisionInstructions."""
        lower = comment.lower().strip()
        instructions: list[RevisionInstruction] = []

        # --- Tone detection (check first, may overlap with section targeting) ---
        tone_action = self._detect_tone(lower)

        # --- Evidence detection ---
        if self._is_evidence_comment(lower):
            # Determine sub-action
            if any(p in lower for p in ["conservative", "cautious", "hedge", "limited evidence"]):
                instructions.append(
                    self._make_instruction(
                        target="tone",
                        action="soften",
                        detail="Apply conservative clinical wording where evidence is limited",
                        parameters={"evidence_driven": True},
                        source=comment,
                    )
                )
            elif any(p in lower for p in ["remove weak", "remove weakly"]):
                instructions.append(
                    self._make_instruction(
                        target="evidence",
                        action="remove",
                        detail="Remove weakly supported claims",
                        parameters={"remove_weak": True},
                        source=comment,
                    )
                )
            elif any(p in lower for p in ["downgrade"]):
                instructions.append(
                    self._make_instruction(
                        target="evidence",
                        action="soften",
                        detail="Downgrade confidence where evidence is insufficient",
                        parameters={"downgrade": True},
                        source=comment,
                    )
                )
            else:
                instructions.append(
                    self._make_instruction(
                        target="evidence",
                        action="update",
                        detail="Update references with more recent evidence",
                        parameters={"newer": True},
                        source=comment,
                    )
                )
            # May also contain section targeting, so continue

        # --- Modality detection ---
        modality = self._detect_modality(lower)
        action = self._detect_action(lower)

        if modality:
            mod_action = action if action in ("remove", "add") else self._infer_modality_action(lower)
            instructions.append(
                self._make_instruction(
                    target="modality",
                    action=mod_action,
                    detail=f"{mod_action.capitalize()} modality {modality}",
                    parameters={"modality": modality},
                    source=comment,
                )
            )
            # If modality was the main content, return early unless there's
            # an independent tone or evidence instruction to add
            if not tone_action:
                return instructions

        # --- Section targeting ---
        section_id = self._detect_section(lower, section_ids)

        if tone_action and section_id:
            instructions.append(
                self._make_instruction(
                    target=f"section:{section_id}",
                    action=tone_action,
                    section_id=section_id,
                    detail=f"{tone_action.capitalize()} language in {section_id} section",
                    source=comment,
                )
            )
        elif tone_action:
            instructions.append(
                self._make_instruction(
                    target="tone",
                    action=tone_action,
                    detail=f"{tone_action.capitalize()} overall tone",
                    source=comment,
                )
            )
        elif section_id and action:
            params: dict = {}
            if action == "shorten":
                params["shorter"] = True
            elif action == "expand":
                params["expand"] = True

            # Detect if this targets a table within the section
            is_table = "table" in lower
            target = f"table:{section_id}" if is_table else f"section:{section_id}"

            instructions.append(
                self._make_instruction(
                    target=target,
                    action=action,
                    section_id=section_id,
                    detail=f"{action.capitalize()} {section_id}",
                    parameters=params,
                    source=comment,
                )
            )
        elif action and not modality and not self._is_evidence_comment(lower):
            # Generic action on the whole document
            instructions.append(
                self._make_instruction(
                    target="document",
                    action=action,
                    detail=f"{action.capitalize()} document: {comment}",
                    source=comment,
                )
            )

        return instructions

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _detect_action(self, lower: str) -> str:
        """Detect the primary action from comment text."""
        # Check multi-word phrases first (longest match wins)
        for phrase in sorted(_ACTION_KEYWORDS, key=len, reverse=True):
            if phrase in lower:
                return _ACTION_KEYWORDS[phrase]
        return ""

    def _detect_modality(self, lower: str) -> str:
        """Detect a modality token in the comment."""
        for token, canonical in _MODALITY_TOKENS.items():
            # Match as whole word
            if re.search(rf"\b{re.escape(token)}\b", lower):
                return canonical
        return ""

    def _infer_modality_action(self, lower: str) -> str:
        """When a modality is mentioned without a clear action, infer one."""
        negatives = ("no ", "without ", "exclude ", "not ")
        for neg in negatives:
            if neg in lower:
                return "remove"
        if "add" in lower or "include" in lower:
            return "add"
        return "remove"  # default: mentioning a modality alone usually means remove

    def _detect_section(self, lower: str, section_ids: list[str] | None) -> str:
        """Detect a section reference in the comment."""
        # Check known aliases (longest first for greedy matching)
        for alias in sorted(_SECTION_ALIASES, key=len, reverse=True):
            if alias in lower:
                return _SECTION_ALIASES[alias]

        # Check provided section_ids directly
        if section_ids:
            for sid in section_ids:
                if sid.lower() in lower:
                    return sid

        return ""

    def _detect_tone(self, lower: str) -> str:
        """Detect tone-adjustment phrases."""
        for phrase, action in _TONE_PHRASES:
            if phrase in lower:
                return action
        return ""

    def _is_evidence_comment(self, lower: str) -> bool:
        """Check if the comment relates to evidence/references."""
        return any(phrase in lower for phrase in _EVIDENCE_PHRASES)

    def _make_instruction(
        self,
        target: str,
        action: str,
        detail: str,
        source: str,
        section_id: str | None = None,
        parameters: dict | None = None,
        priority: str = "normal",
    ) -> RevisionInstruction:
        """Build a RevisionInstruction with a fresh ID."""
        return RevisionInstruction(
            instruction_id=uuid.uuid4().hex[:12],
            target=target,
            action=action,
            section_id=section_id,
            detail=detail,
            parameters=parameters or {},
            priority=priority,
            source_comment=source,
        )
