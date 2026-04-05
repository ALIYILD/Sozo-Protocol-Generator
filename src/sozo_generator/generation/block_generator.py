"""Block-level content generator for the SOZO long-document production pipeline.

Generates individual CanonicalBlock objects from ContentBlockSpec instances
by dispatching on block_type and mapping content_hint values to structured
ConditionSchema fields. No LLM calls are made in this version; all content
is assembled deterministically from condition data.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from ..schemas.canonical import CanonicalBlock, ContentBlockSpec
from ..schemas.condition import ConditionSchema

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Word-count helpers
# ---------------------------------------------------------------------------

_WORDS_PER_SENTENCE = 18  # rough estimate used for padding decisions


def _sentence_count(text: str) -> int:
    """Approximate sentence count by splitting on terminal punctuation."""
    import re
    return max(1, len(re.split(r"(?<=[.!?])\s+", text.strip())))


def _word_count(text: str) -> int:
    return len(text.split()) if text else 0


def _trim_to_word_count(text: str, target: int) -> str:
    """Return the text, trimming by whole sentences if well over target.

    The trim is intentionally conservative: we only cut when the text is
    more than 50 % over target, and we always keep at least two sentences.
    """
    if target <= 0 or _word_count(text) <= target * 1.5:
        return text

    import re
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    result: list[str] = []
    wc = 0
    for sent in sentences:
        sw = _word_count(sent)
        if wc + sw > target * 1.5 and len(result) >= 2:
            break
        result.append(sent)
        wc += sw
    return " ".join(result)


# ---------------------------------------------------------------------------
# List / bullet formatting
# ---------------------------------------------------------------------------

def _format_bullet_list(items: list[str], prefix: str = "•") -> str:
    """Format a list of strings as a bullet list."""
    if not items:
        return ""
    return "\n".join(f"{prefix} {item}" for item in items)


def _format_numbered_list(items: list[str]) -> str:
    """Format a list of strings as a numbered list."""
    if not items:
        return ""
    return "\n".join(f"{i + 1}. {item}" for i, item in enumerate(items))


# ---------------------------------------------------------------------------
# Reference formatting
# ---------------------------------------------------------------------------

def _format_references(references: list[dict]) -> str:
    """Format condition.references as a numbered reference list."""
    if not references:
        return "[No references available]"
    lines: list[str] = []
    for i, ref in enumerate(references, start=1):
        authors = ref.get("authors", ref.get("authors_short", "Unknown authors"))
        year = ref.get("year", "")
        title = ref.get("title", "Untitled")
        journal = ref.get("journal", "")
        pmid = ref.get("pmid", "")
        line = f"{i}. {authors}"
        if year:
            line += f" ({year})"
        line += f". {title}."
        if journal:
            line += f" {journal}."
        if pmid:
            line += f" PMID: {pmid}."
        lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Network profile narrative
# ---------------------------------------------------------------------------

def _describe_network_profiles(condition: ConditionSchema) -> str:
    """Compose a narrative paragraph from network_profiles."""
    if not condition.network_profiles:
        return ""
    parts: list[str] = []
    for np in condition.network_profiles:
        dysfunction_label = {
            "hypo": "hypoactivity",
            "hyper": "hyperactivity",
            "normal": "normal activity",
        }.get(str(np.dysfunction.value) if hasattr(np.dysfunction, "value") else str(np.dysfunction), "dysfunction")
        network_label = np.network.value.upper() if hasattr(np.network, "value") else str(np.network).upper()
        sev = np.severity if np.severity else "moderate"
        relevance = np.relevance if np.relevance else ""
        desc = f"The {network_label} exhibits {sev} {dysfunction_label}"
        if relevance:
            desc += f": {relevance}"
        desc += "."
        parts.append(desc)
    return " ".join(parts)


def _describe_stimulation_targets(condition: ConditionSchema) -> str:
    """Compose a summary of stimulation targets."""
    if not condition.stimulation_targets:
        return ""
    parts: list[str] = []
    for st in condition.stimulation_targets:
        modality = st.modality.value.upper() if hasattr(st.modality, "value") else str(st.modality).upper()
        target = st.target_region
        abbrev = st.target_abbreviation
        laterality = st.laterality
        rationale = st.rationale
        off_label_note = " (off-label)" if st.off_label else ""
        line = (
            f"{modality} targeting {target} ({abbrev}), {laterality}{off_label_note}. "
            f"{rationale}"
        )
        parts.append(line)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# BlockGenerator
# ---------------------------------------------------------------------------

class BlockGenerator:
    """Generates individual CanonicalBlock objects from ContentBlockSpec.

    Text blocks are generated from structured condition data — NOT from
    LLM calls in this version. Content is assembled from ConditionSchema fields.
    Future: plug in LLM generation per block.
    """

    def generate(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,  # "fellow" | "partners"
        asset_registry: Optional[Any] = None,
    ) -> CanonicalBlock:
        """Dispatch based on spec.block_type and return a CanonicalBlock."""
        bt = spec.block_type

        if bt == "text":
            return self._generate_text_block(spec, condition, variant)
        elif bt == "list":
            return self._generate_list_block(spec, condition, variant)
        elif bt == "callout":
            return self._generate_callout_block(spec, condition, variant)
        elif bt == "heading":
            return self._generate_heading_block(spec)
        elif bt == "divider":
            return self._generate_divider_block(spec)
        elif bt in ("table", "figure", "chart", "image"):
            return self._generate_asset_placeholder_block(spec, asset_registry)
        else:
            # Unknown type — create a minimal placeholder
            logger.debug("BlockGenerator: unknown block_type '%s', creating placeholder.", bt)
            return CanonicalBlock(
                block_id=spec.block_id,
                block_type=bt,  # type: ignore[arg-type]
                heading=spec.heading,
                heading_level=spec.heading_level,
                content=f"[{spec.content_hint}]" if spec.content_hint else None,
                asset_id=spec.asset_id,
                placeholder_resolved=False,
                metadata=dict(spec.metadata),
                generation_metadata={"content_hint": spec.content_hint, "variant": variant},
            )

    # ------------------------------------------------------------------
    # Text block
    # ------------------------------------------------------------------

    def _generate_text_block(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalBlock:
        """Generate text content from condition data based on content_hint."""
        hint = (spec.content_hint or "").strip().lower()
        target_wc = spec.target_word_count
        placeholder_resolved = True
        content: str

        # ── Core clinical content ─────────────────────────────────────
        if hint in ("overview", "condition_overview"):
            name = condition.display_name or "this condition"
            icd = condition.icd10 or ""
            icd_clause = f" (ICD-10: {icd})" if icd else ""
            overview = condition.overview or f"[Overview not yet available for {name}]"
            content = f"{name}{icd_clause}\n\n{overview}"

        elif hint == "pathophysiology":
            content = condition.pathophysiology or (
                f"[Pathophysiology data not yet available for {condition.display_name}]"
            )

        elif hint == "evidence_summary":
            summary = condition.evidence_summary or ""
            gaps = condition.evidence_gaps or []
            parts = [summary] if summary else []
            if gaps:
                gap_text = "Evidence gaps include: " + "; ".join(gaps) + "."
                parts.append(gap_text)
            content = "\n\n".join(parts) if parts else (
                f"[Evidence summary not yet available for {condition.display_name}]"
            )

        elif hint == "fnon_rationale":
            if variant == "partners":
                content = condition.fnon_rationale or (
                    f"[FNON rationale not yet defined for {condition.display_name}]"
                )
            else:
                # Fellow variant — simplified rationale
                base = condition.fnon_rationale or ""
                content = base if base else (
                    f"Neuromodulation targets the functional networks implicated in "
                    f"{condition.display_name} to restore adaptive neural activity."
                )

        elif hint == "treatment_rationale":
            proto_rationale = ""
            if condition.protocols:
                proto_rationale = condition.protocols[0].rationale
            ev = condition.evidence_summary or ""
            parts = [proto_rationale, ev]
            content = "\n\n".join(p for p in parts if p) or (
                f"[Treatment rationale not yet available for {condition.display_name}]"
            )

        elif hint == "stimulation_overview":
            content = _describe_stimulation_targets(condition) or (
                f"[Stimulation targets not yet defined for {condition.display_name}]"
            )

        elif hint == "qeeg_interpretation":
            content = _describe_network_profiles(condition) or (
                f"[Network/qEEG interpretation not yet available for {condition.display_name}]"
            )

        elif hint == "session_schedule":
            if condition.protocols:
                p = condition.protocols[0]
                sc = p.session_count
                notes = p.notes or ""
                session_clause = f"{sc} sessions" if sc else "variable session count"
                content = (
                    f"The standard protocol for {condition.display_name} comprises "
                    f"{session_clause} of {p.label}."
                )
                if notes:
                    content += f" {notes}"
            else:
                content = f"[Session schedule not yet defined for {condition.display_name}]"

        elif hint == "monitoring_tracking":
            criteria = condition.responder_criteria or []
            tools = condition.assessment_tools or []
            parts: list[str] = []
            if criteria:
                parts.append(
                    "Responder criteria: " + "; ".join(criteria) + "."
                )
            if tools:
                tool_names = [f"{t.name} ({t.abbreviation})" for t in tools]
                parts.append(
                    "Assessment instruments: " + ", ".join(tool_names) + "."
                )
            content = "\n\n".join(parts) if parts else (
                f"[Monitoring and tracking data not yet defined for {condition.display_name}]"
            )

        elif hint == "clinician_workflow":
            tips = condition.clinical_tips or []
            rules = condition.governance_rules or []
            parts = []
            if tips:
                parts.append("Clinical tips:\n" + _format_bullet_list(tips))
            if rules:
                parts.append("Governance rules:\n" + _format_bullet_list(rules))
            content = "\n\n".join(parts) if parts else (
                f"[Clinician workflow not yet defined for {condition.display_name}]"
            )

        elif hint == "safety_overview":
            notes = condition.safety_notes or []
            contras = condition.contraindications or []
            parts = []
            if notes:
                note_lines = [f"• [{n.severity.upper()}] {n.description}" for n in notes]
                parts.append("Safety considerations:\n" + "\n".join(note_lines))
            if contras:
                parts.append("Contraindications:\n" + _format_bullet_list(contras))
            content = "\n\n".join(parts) if parts else (
                f"[Safety information not yet defined for {condition.display_name}]"
            )

        elif hint == "medication_interactions":
            levo = condition.levodopa_note or ""
            notes = condition.safety_notes or []
            med_notes = [n.description for n in notes if "medic" in n.category.lower() or "drug" in n.category.lower()]
            parts = []
            if levo:
                parts.append(levo)
            if med_notes:
                parts.append("\n".join(f"• {m}" for m in med_notes))
            if not parts:
                # Fallback to general safety notes
                if notes:
                    parts.append(
                        "Relevant safety notes:\n"
                        + "\n".join(f"• {n.description}" for n in notes[:5])
                    )
            content = "\n\n".join(parts) if parts else (
                f"[Medication interaction information not yet defined for {condition.display_name}]"
            )

        elif hint == "partner_fnon_advanced":
            if variant == "partners":
                fnon = condition.fnon_rationale or ""
                network_desc = _describe_network_profiles(condition)
                parts = [p for p in [fnon, network_desc] if p]
                content = "\n\n".join(parts) if parts else (
                    f"[Advanced FNON content not yet defined for {condition.display_name}]"
                )
            else:
                # Not applicable for fellow
                content = ""

        elif hint == "appendix_references":
            content = _format_references(condition.references)

        elif hint == "responder_criteria":
            criteria = condition.responder_criteria or []
            if criteria:
                content = "Responder criteria:\n" + _format_bullet_list(criteria)
            else:
                content = f"[Responder criteria not yet defined for {condition.display_name}]"

        elif hint == "clinical_tips":
            tips = condition.clinical_tips or []
            if tips:
                content = "Clinical tips:\n" + _format_bullet_list(tips)
            else:
                content = f"[Clinical tips not yet defined for {condition.display_name}]"

        elif hint == "governance_rules":
            rules = condition.governance_rules or []
            if rules:
                content = "Governance rules:\n" + _format_bullet_list(rules)
            else:
                content = f"[Governance rules not yet defined for {condition.display_name}]"

        elif hint == "non_responder_pathway":
            content = condition.non_responder_pathway or (
                f"[Non-responder pathway not yet defined for {condition.display_name}]"
            )

        elif hint == "safety_notes":
            notes = condition.safety_notes or []
            if notes:
                lines = [f"• [{n.category}] {n.description}" for n in notes]
                content = "\n".join(lines)
            else:
                content = f"[Safety notes not yet defined for {condition.display_name}]"

        elif hint == "inclusion_criteria":
            items = condition.inclusion_criteria or []
            if items:
                content = "Inclusion criteria:\n" + _format_bullet_list(items)
            else:
                content = f"[Inclusion criteria not yet defined for {condition.display_name}]"

        elif hint == "exclusion_criteria":
            items = condition.exclusion_criteria or []
            if items:
                content = "Exclusion criteria:\n" + _format_bullet_list(items)
            else:
                content = f"[Exclusion criteria not yet defined for {condition.display_name}]"

        elif hint == "core_symptoms":
            items = condition.core_symptoms or []
            if items:
                content = "Core symptoms:\n" + _format_bullet_list(items)
            else:
                content = f"[Core symptoms not yet defined for {condition.display_name}]"

        else:
            # Unrecognized hint — return placeholder
            placeholder_resolved = False
            raw = spec.content_hint or hint
            content = f"[{raw}]"
            logger.debug(
                "BlockGenerator: unrecognized content_hint '%s', emitting placeholder.", hint
            )

        # Apply word-count trim (conservative)
        if target_wc > 0 and content:
            content = _trim_to_word_count(content, target_wc)

        return CanonicalBlock(
            block_id=spec.block_id,
            block_type="text",
            heading=spec.heading,
            heading_level=spec.heading_level,
            content=content or None,
            placeholder_resolved=placeholder_resolved,
            metadata=dict(spec.metadata),
            generation_metadata={
                "content_hint": spec.content_hint,
                "variant": variant,
                "target_word_count": target_wc,
            },
        )

    # ------------------------------------------------------------------
    # List block
    # ------------------------------------------------------------------

    def _generate_list_block(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalBlock:
        """Generate a formatted list block."""
        hint = (spec.content_hint or "").strip().lower()
        items: list[str] = []
        placeholder_resolved = True

        if hint in ("core_symptoms", "symptoms"):
            items = condition.core_symptoms or []
        elif hint == "non_motor_symptoms":
            items = condition.non_motor_symptoms or []
        elif hint == "inclusion_criteria":
            items = condition.inclusion_criteria or []
        elif hint == "exclusion_criteria":
            items = condition.exclusion_criteria or []
        elif hint == "contraindications":
            items = condition.contraindications or []
        elif hint == "clinical_tips":
            items = condition.clinical_tips or []
        elif hint == "governance_rules":
            items = condition.governance_rules or []
        elif hint == "responder_criteria":
            items = condition.responder_criteria or []
        elif hint == "evidence_gaps":
            items = condition.evidence_gaps or []
        elif hint == "key_brain_regions":
            items = condition.key_brain_regions or []
        elif hint == "decision_tree_notes":
            items = condition.decision_tree_notes or []
        elif hint == "assessment_tools":
            items = [
                f"{t.name} ({t.abbreviation}) — {t.timing}"
                for t in (condition.assessment_tools or [])
            ]
        else:
            placeholder_resolved = False
            content = f"[{spec.content_hint}]" if spec.content_hint else "[list placeholder]"
            return CanonicalBlock(
                block_id=spec.block_id,
                block_type="list",
                heading=spec.heading,
                heading_level=spec.heading_level,
                content=content,
                placeholder_resolved=False,
                metadata=dict(spec.metadata),
                generation_metadata={"content_hint": spec.content_hint, "variant": variant},
            )

        if items:
            content = _format_bullet_list(items)
        else:
            placeholder_resolved = False
            content = f"[{hint} list — no data available]"

        return CanonicalBlock(
            block_id=spec.block_id,
            block_type="list",
            heading=spec.heading,
            heading_level=spec.heading_level,
            content=content,
            placeholder_resolved=placeholder_resolved,
            metadata=dict(spec.metadata),
            generation_metadata={"content_hint": spec.content_hint, "variant": variant},
        )

    # ------------------------------------------------------------------
    # Callout block
    # ------------------------------------------------------------------

    def _generate_callout_block(
        self,
        spec: ContentBlockSpec,
        condition: ConditionSchema,
        variant: str,
    ) -> CanonicalBlock:
        """Generate a callout/highlight block (clinical tip, warning, etc.)."""
        hint = (spec.content_hint or "").strip().lower()
        placeholder_resolved = True
        content: str

        if hint in ("clinical_tip", "clinical_tips"):
            tips = condition.clinical_tips or []
            if tips:
                content = tips[0]  # Use the first clinical tip as a callout
            else:
                placeholder_resolved = False
                content = f"[Clinical tip — not yet defined for {condition.display_name}]"

        elif hint == "safety_warning":
            notes = condition.safety_notes or []
            high_sev = [n for n in notes if n.severity in ("high", "absolute")]
            if high_sev:
                content = f"WARNING: {high_sev[0].description}"
            elif notes:
                content = f"NOTE: {notes[0].description}"
            else:
                placeholder_resolved = False
                content = f"[Safety warning — not yet defined for {condition.display_name}]"

        elif hint == "governance_callout":
            rules = condition.governance_rules or []
            if rules:
                content = rules[0]
            else:
                placeholder_resolved = False
                content = f"[Governance callout — not yet defined for {condition.display_name}]"

        elif hint == "evidence_callout":
            ev = condition.evidence_summary or ""
            if ev:
                # First sentence only for a callout
                import re
                sentences = re.split(r"(?<=[.!?])\s+", ev.strip())
                content = sentences[0] if sentences else ev
            else:
                placeholder_resolved = False
                content = f"[Evidence callout — not yet defined for {condition.display_name}]"

        elif hint == "off_label_notice":
            off_label_protocols = [p for p in (condition.protocols or []) if p.off_label]
            if off_label_protocols:
                mods = list({
                    (p.modality.value.upper() if hasattr(p.modality, "value") else str(p.modality).upper())
                    for p in off_label_protocols
                })
                content = (
                    f"IMPORTANT: {', '.join(mods)} applications for {condition.display_name} "
                    f"are OFF-LABEL. Explicit informed consent is required."
                )
            else:
                content = (
                    f"All protocols for {condition.display_name} require clinician "
                    f"assessment and appropriate patient consent."
                )

        else:
            # Fallback — delegate to text block generation
            text_block = self._generate_text_block(spec, condition, variant)
            return CanonicalBlock(
                block_id=spec.block_id,
                block_type="callout",
                heading=spec.heading,
                heading_level=spec.heading_level,
                content=text_block.content,
                placeholder_resolved=text_block.placeholder_resolved,
                metadata=dict(spec.metadata),
                generation_metadata={"content_hint": spec.content_hint, "variant": variant},
            )

        return CanonicalBlock(
            block_id=spec.block_id,
            block_type="callout",
            heading=spec.heading,
            heading_level=spec.heading_level,
            content=content,
            placeholder_resolved=placeholder_resolved,
            metadata=dict(spec.metadata),
            generation_metadata={"content_hint": spec.content_hint, "variant": variant},
        )

    # ------------------------------------------------------------------
    # Heading block
    # ------------------------------------------------------------------

    def _generate_heading_block(self, spec: ContentBlockSpec) -> CanonicalBlock:
        """Generate a heading block."""
        content = spec.heading or spec.content_hint or ""
        return CanonicalBlock(
            block_id=spec.block_id,
            block_type="heading",
            heading=spec.heading,
            heading_level=spec.heading_level if spec.heading_level > 0 else 1,
            content=content,
            placeholder_resolved=bool(content),
            metadata=dict(spec.metadata),
            generation_metadata={"content_hint": spec.content_hint},
        )

    # ------------------------------------------------------------------
    # Divider block
    # ------------------------------------------------------------------

    def _generate_divider_block(self, spec: ContentBlockSpec) -> CanonicalBlock:
        """Generate a divider block."""
        return CanonicalBlock(
            block_id=spec.block_id,
            block_type="divider",
            heading=None,
            heading_level=0,
            content=None,
            placeholder_resolved=True,
            metadata=dict(spec.metadata),
        )

    # ------------------------------------------------------------------
    # Asset placeholder block (table / figure / chart / image)
    # ------------------------------------------------------------------

    def _generate_asset_placeholder_block(
        self,
        spec: ContentBlockSpec,
        asset_registry: Optional[Any],
    ) -> CanonicalBlock:
        """Create a placeholder block referencing an asset by ID."""
        asset_record = None
        if asset_registry is not None and spec.asset_id:
            try:
                asset_record = asset_registry.get(spec.asset_id)
            except Exception:
                logger.debug(
                    "BlockGenerator: could not look up asset '%s' in registry.", spec.asset_id
                )

        placeholder_resolved = spec.asset_id is not None

        return CanonicalBlock(
            block_id=spec.block_id,
            block_type=spec.block_type,  # type: ignore[arg-type]
            heading=spec.heading,
            heading_level=spec.heading_level,
            content=None,
            asset_id=spec.asset_id,
            asset_record=asset_record,
            placeholder_resolved=placeholder_resolved,
            metadata=dict(spec.metadata),
            generation_metadata={
                "content_hint": spec.content_hint,
                "asset_type": spec.block_type,
            },
        )
