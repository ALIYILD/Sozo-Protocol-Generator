"""
Section Writer — generates draft content for each section of a template-driven document.

Supports multiple generation strategies:
1. **data_driven**: Build content directly from ConditionSchema data (tables, lists, etc.)
2. **template_adapt**: Adapt harvested content from the content library
3. **ai_draft**: Use LLM to draft prose grounded in evidence brief

The writer NEVER fabricates PMIDs, clinical claims, or unsupported evidence.
All AI-generated content is marked for review.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from ..template_profiles.models import DraftedSection, SectionBrief

logger = logging.getLogger(__name__)


class SectionWriter:
    """Writes section content using the most appropriate strategy.

    Strategy selection:
    - If section has rich internal data → data_driven (tables, lists from ConditionSchema)
    - If content library has matching content → template_adapt (rewrite for target condition)
    - If section needs evidence-grounded prose → ai_draft (LLM with brief)
    - Fallback → placeholder with review flag

    Usage:
        writer = SectionWriter(anthropic_api_key="sk-...")
        drafted = writer.write_section(brief)
    """

    def __init__(
        self,
        anthropic_api_key: str = "",
        openai_api_key: str = "",
        prefer_data_driven: bool = True,
    ):
        self.anthropic_key = anthropic_api_key
        self.openai_key = openai_api_key
        self.prefer_data = prefer_data_driven

    def write_section(self, brief: SectionBrief) -> DraftedSection:
        """Write content for a single section based on its brief."""
        section = brief.section_spec

        # Choose strategy
        if self.prefer_data and self._has_rich_data(brief):
            return self._write_data_driven(brief)

        if self._has_harvested_content(brief):
            return self._write_template_adapt(brief)

        if (self.anthropic_key or self.openai_key) and section.requires_evidence:
            return self._write_ai_draft(brief)

        # Fallback: data-driven even for sparse data
        return self._write_data_driven(brief)

    def write_all(self, briefs: list[SectionBrief]) -> list[DraftedSection]:
        """Write all sections."""
        return [self.write_section(b) for b in briefs]

    def _has_rich_data(self, brief: SectionBrief) -> bool:
        """Check if brief has enough internal data for data-driven generation."""
        data = brief.internal_condition_data
        # Count non-empty fields
        rich_fields = sum(
            1 for v in data.values()
            if v and (isinstance(v, str) and len(v) > 20 or isinstance(v, list) and len(v) > 0)
        )
        return rich_fields >= 2

    def _has_harvested_content(self, brief: SectionBrief) -> bool:
        """Check if content library has matching content."""
        # Check if any source is from content library
        for cite in brief.citations_available:
            if "harvested" in str(cite.get("title", "")).lower():
                return True
        return False

    def _write_data_driven(self, brief: SectionBrief) -> DraftedSection:
        """Build section content directly from structured condition data."""
        section = brief.section_spec
        data = brief.internal_condition_data
        parts = []
        tables = []
        citations = []

        condition_name = data.get("condition_name", brief.target_condition_name)

        # Build content based on what data is available
        if "overview" in data:
            parts.append(data["overview"])
        if "pathophysiology" in data:
            parts.append(data["pathophysiology"])
        if "core_symptoms" in data and data["core_symptoms"]:
            parts.append(f"Core clinical features of {condition_name} include:")
            for symptom in data["core_symptoms"]:
                parts.append(f"- {symptom}")

        if "brain_regions" in data and data["brain_regions"]:
            parts.append(f"\nKey brain regions implicated in {condition_name}:")
            for region in data["brain_regions"]:
                desc = data.get("brain_descriptions", {}).get(region, "")
                parts.append(f"- {region}: {desc}" if desc else f"- {region}")

        if "network_profiles" in data and data["network_profiles"]:
            parts.append(f"\nFunctional network involvement in {condition_name}:")
            table_rows = [["Network", "Dysfunction", "Severity", "Relevance"]]
            for np in data["network_profiles"]:
                table_rows.append([
                    np["network"].upper(),
                    np["dysfunction"],
                    np["severity"],
                    np.get("relevance", "")[:80],
                ])
            tables.append({"headers": table_rows[0], "rows": table_rows[1:], "caption": "FNON Network Profile"})

        if "phenotypes" in data and data["phenotypes"]:
            parts.append(f"\nClinical phenotype subtypes for {condition_name}:")
            table_rows = [["Phenotype", "Key Features", "Primary Networks"]]
            for p in data["phenotypes"]:
                features = "; ".join(p.get("key_features", [])[:3])
                networks = ", ".join(p.get("primary_networks", []))
                table_rows.append([p.get("label", ""), features, networks])
            tables.append({"headers": table_rows[0], "rows": table_rows[1:], "caption": "Phenotype Classification"})

        if "protocols" in data and data["protocols"]:
            parts.append(f"\nStimulation protocols for {condition_name}:")
            table_rows = [["Protocol", "Modality", "Target", "Evidence Level"]]
            for p in data["protocols"]:
                table_rows.append([
                    p.get("label", ""),
                    p.get("modality", "").upper(),
                    p.get("target_region", ""),
                    p.get("evidence_level", ""),
                ])
                if p.get("off_label"):
                    parts.append(f"Note: {p.get('modality', '')} use is OFF-LABEL and requires informed consent.")
            tables.append({"headers": table_rows[0], "rows": table_rows[1:], "caption": "Protocol Summary"})

        if "safety_notes" in data and data["safety_notes"]:
            parts.append("\nSafety considerations:")
            for note in data["safety_notes"]:
                parts.append(f"- [{note['severity'].upper()}] {note['description']}")

        if "assessment_tools" in data and data["assessment_tools"]:
            table_rows = [["Scale", "Abbreviation", "Domains", "Timing"]]
            for t in data["assessment_tools"]:
                table_rows.append([
                    t["name"], t["abbreviation"],
                    ", ".join(t.get("domains", [])), t.get("timing", ""),
                ])
            tables.append({"headers": table_rows[0], "rows": table_rows[1:], "caption": "Assessment Tools"})

        if "inclusion_criteria" in data and data["inclusion_criteria"]:
            parts.append("\nInclusion criteria:")
            for c in data["inclusion_criteria"]:
                parts.append(f"- {c}")

        if "exclusion_criteria" in data and data["exclusion_criteria"]:
            parts.append("\nExclusion criteria:")
            for c in data["exclusion_criteria"]:
                parts.append(f"- {c}")

        if "references" in data and data["references"]:
            for ref in data["references"]:
                pmid = ref.get("pmid", "")
                if pmid and not str(pmid).startswith("placeholder"):
                    citations.append(str(pmid))

        content = "\n".join(parts) if parts else ""
        needs_review = not content

        return DraftedSection(
            section_id=section.section_id,
            title=section.title,
            content=content,
            tables=tables,
            citations_used=citations,
            claim_count=len([p for p in parts if any(kw in p.lower() for kw in ["evidence", "study", "trial"])]),
            confidence="high" if content else "insufficient",
            review_flags=["INSUFFICIENT DATA — REQUIRES CLINICAL INPUT"] if needs_review else [],
            needs_review=needs_review,
            generation_method="data_driven",
            generation_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def _write_template_adapt(self, brief: SectionBrief) -> DraftedSection:
        """Adapt harvested content from content library for the target condition."""
        section = brief.section_spec
        # Find harvested content in citations
        harvested_content = ""
        for cite in brief.citations_available:
            if "harvested" in str(cite.get("title", "")).lower():
                harvested_content = cite.get("abstract", "")
                break

        if not harvested_content:
            return self._write_data_driven(brief)

        # Simple adaptation: replace condition names
        content = harvested_content
        # This would ideally use AI for smarter adaptation

        return DraftedSection(
            section_id=section.section_id,
            title=section.title,
            content=content,
            confidence="medium",
            review_flags=["Adapted from content library — verify condition specificity"],
            needs_review=True,
            generation_method="template_adapt",
            generation_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def _write_ai_draft(self, brief: SectionBrief) -> DraftedSection:
        """Use LLM to draft section content grounded in the brief."""
        section = brief.section_spec

        # Build the prompt
        prompt = self._build_writing_prompt(brief)

        # Try to call LLM
        content = ""
        model_used = ""

        if self.anthropic_key:
            content, model_used = self._call_anthropic(prompt)
        elif self.openai_key:
            content, model_used = self._call_openai(prompt)

        if not content:
            # Fallback to data-driven
            logger.info(f"AI draft unavailable for {section.section_id}, falling back to data-driven")
            result = self._write_data_driven(brief)
            result.review_flags.append("AI draft unavailable — generated from structured data only")
            return result

        # Extract citation references from generated text
        import re
        pmid_refs = re.findall(r"PMID[:\s]*(\d{7,9})", content)

        return DraftedSection(
            section_id=section.section_id,
            title=section.title,
            content=content,
            citations_used=pmid_refs,
            confidence="medium",
            review_flags=["AI-generated content — requires clinical review"],
            needs_review=True,
            generation_method="ai_draft",
            model_used=model_used,
            generation_timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

    def _build_writing_prompt(self, brief: SectionBrief) -> str:
        """Build a structured prompt for AI section writing."""
        section = brief.section_spec
        data = brief.internal_condition_data

        prompt = f"""You are writing a clinical document section for SOZO Brain Center.

SECTION: {section.title}
CONDITION: {brief.target_condition_name}
TIER: {brief.tier}
DOCUMENT TYPE: {brief.doc_type}

STYLE REQUIREMENTS:
- Audience: {brief.style_constraints.audience}
- Formality: {brief.style_constraints.formality}
- Voice: {brief.style_constraints.voice}
- Section depth: {brief.style_constraints.section_depth}
- Approximate length: {section.estimated_word_count} words

AVAILABLE EVIDENCE:
{brief.evidence_summary}

AVAILABLE CITATIONS (use these PMIDs when referencing evidence):
{json.dumps(brief.citations_available[:10], indent=2)}

CONDITION DATA:
{json.dumps(data, indent=2, default=str)[:3000]}

REQUIRED TOPICS:
{chr(10).join(f"- {t}" for t in brief.required_topics)}

CRITICAL RULES:
- Do NOT fabricate PMIDs or citations
- Do NOT claim regulatory approval without evidence
- Do NOT invent stimulation parameters
- Do NOT make unsupported efficacy claims
- Only reference PMIDs from the AVAILABLE CITATIONS list
- Mark uncertain claims with [REQUIRES REVIEW]
- Use evidence-based language appropriate to the confidence level

Write the section content now. Be specific, clinical, and evidence-grounded."""

        return prompt

    def _call_anthropic(self, prompt: str) -> tuple[str, str]:
        """Call Anthropic Claude API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text, "claude-sonnet-4-20250514"
        except Exception as e:
            logger.warning(f"Anthropic API call failed: {e}")
            return "", ""

    def _call_openai(self, prompt: str) -> tuple[str, str]:
        """Call OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
            )
            return response.choices[0].message.content, "gpt-4o"
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}")
            return "", ""
