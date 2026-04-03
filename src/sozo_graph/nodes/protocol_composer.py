"""
protocol_composer — LLM node that generates prose sections grounded in evidence.

Type: LLM node (structured output)
Does NOT choose stimulation parameters — those come from base_sequence.
The LLM writes rationale text, clinical context, and narrative sections.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from pydantic import BaseModel, Field

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


# ── Output schema ──────────────────────────────────────────────────────


class ProtocolClaim(BaseModel):
    claim_text: str
    evidence_ids: list[str] = Field(..., min_length=1)
    claim_type: str  # supports | informs | contradicts | safety_note
    confidence: str  # high | medium | low
    uncertainty_flag: Optional[str] = None


class ComposedSection(BaseModel):
    section_id: str
    title: str
    content: str
    cited_evidence_ids: list[str] = Field(default_factory=list)
    confidence: str = "medium"
    generation_method: str = "llm_composed"
    claims: list[ProtocolClaim] = Field(default_factory=list)


class ComposerOutput(BaseModel):
    sections: list[ComposedSection]


# ── System prompt ──────────────────────────────────────────────────────

COMPOSER_SYSTEM_PROMPT = """You are Sozo's protocol composition engine. You write clinical protocol document sections grounded in evidence.

CRITICAL RULES:
1. Every factual claim MUST cite at least one evidence_id from the provided evidence_pool.
2. Evidence IDs are PMIDs or DOIs. Use the EXACT IDs from the evidence_pool — do NOT fabricate PMIDs.
3. If evidence for a claim is weak (Grade C or D), you MUST include an uncertainty_flag explaining the limitation.
4. If evidence is conflicting, you MUST note the conflict and cite both sides.
5. You do NOT choose stimulation parameters. Those come from the base_sequence provided. You describe and justify them.
6. You MUST NOT claim any modality is "FDA-approved" for neuromodulation indications unless explicitly stated in the evidence.
7. You MUST flag off-label use per the safety_assessment provided.
8. Return ONLY valid JSON matching the output schema. No markdown, no prose wrapper.

Tone: Clinical, precise, evidence-based. Third-person professional voice.
Target audience: Qualified clinicians operating neuromodulation equipment.

OUTPUT FORMAT:
{
  "sections": [
    {
      "section_id": "string",
      "title": "string",
      "content": "Clinical prose with inline citations like (PMID: 12345678)",
      "cited_evidence_ids": ["12345678", "10.1001/example"],
      "confidence": "high|medium|low|insufficient",
      "generation_method": "llm_composed",
      "claims": [
        {
          "claim_text": "Specific claim made in this section",
          "evidence_ids": ["12345678"],
          "claim_type": "supports|informs|contradicts|safety_note",
          "confidence": "high|medium|low",
          "uncertainty_flag": null or "Explanation of limitation"
        }
      ]
    }
  ]
}"""


@audited_node("protocol_composer")
def protocol_composer(state: SozoGraphState) -> dict:
    """Compose protocol sections using LLM with structured output."""
    decisions = []
    condition = state.get("condition", {})
    evidence = state.get("evidence", {})
    protocol = state.get("protocol", {})
    safety = state.get("safety", {})

    articles = evidence.get("articles", [])
    base_sequence = protocol.get("base_sequence", {})

    # Build evidence pool summary for the LLM
    evidence_pool = []
    for a in articles[:30]:  # top 30 by score
        evidence_pool.append({
            "id": a.get("pmid") or a.get("doi") or "",
            "title": a.get("title", ""),
            "authors": a.get("authors", [])[:3],
            "year": a.get("year"),
            "grade": a.get("evidence_grade", "D"),
            "abstract_excerpt": (a.get("abstract") or "")[:300],
        })

    # Build user message
    user_message = json.dumps({
        "condition": {
            "slug": condition.get("slug"),
            "display_name": condition.get("display_name"),
            "icd10": condition.get("icd10"),
        },
        "base_sequence_summary": {
            "phases": len(base_sequence.get("phases", [])),
            "modalities": base_sequence.get("all_modalities", []),
            "total_duration_min": base_sequence.get("total_duration_min"),
        },
        "evidence_pool": evidence_pool,
        "safety_flags": {
            "off_label_flags": safety.get("off_label_flags", []),
            "consent_requirements": safety.get("consent_requirements", []),
            "warnings": safety.get("proceed_with_warnings", []),
        },
        "sections_to_compose": [
            {"section_id": "overview", "title": "Clinical Overview"},
            {"section_id": "pathophysiology", "title": "Pathophysiology & Rationale"},
            {"section_id": "stimulation_protocol", "title": "Stimulation Protocol"},
            {"section_id": "safety_monitoring", "title": "Safety & Monitoring"},
            {"section_id": "outcome_measures", "title": "Outcome Measures"},
        ],
    }, default=str)

    # Call LLM
    try:
        from sozo_generator.core.settings import get_settings
        settings = get_settings()

        if not settings.anthropic_api_key:
            decisions.append("No Anthropic API key — falling back to data-driven composition")
            return _fallback_compose(state, decisions)

        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            system=COMPOSER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text = response.content[0].text

        # Parse and validate
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if match:
                parsed = json.loads(match.group())
            else:
                raise ValueError("LLM response is not valid JSON")

        output = ComposerOutput.model_validate(parsed)

        # Serialize sections
        composed = [s.model_dump() for s in output.sections]
        total_citations = sum(len(s.cited_evidence_ids) for s in output.sections)

        decisions.append(
            f"LLM composed {len(output.sections)} sections with {total_citations} citations"
        )

        return {
            "protocol": {
                **protocol,
                "composed_sections": composed,
            },
            "_decisions": decisions,
        }

    except Exception as e:
        logger.error("LLM composition failed: %s", e)
        decisions.append(f"LLM composition failed: {e} — falling back to data-driven")
        return _fallback_compose(state, decisions)


def _fallback_compose(state: dict, decisions: list) -> dict:
    """Fallback: build sections from condition data without LLM."""
    condition = state.get("condition", {})
    schema_dict = condition.get("schema_dict", {})
    protocol = state.get("protocol", {})

    sections = [
        {
            "section_id": "overview",
            "title": "Clinical Overview",
            "content": schema_dict.get("overview", "[REVIEW REQUIRED: No overview available]"),
            "cited_evidence_ids": [],
            "confidence": "medium",
            "generation_method": "data_driven",
            "claims": [],
        },
        {
            "section_id": "pathophysiology",
            "title": "Pathophysiology & Rationale",
            "content": schema_dict.get("pathophysiology", "[REVIEW REQUIRED]"),
            "cited_evidence_ids": [],
            "confidence": "medium",
            "generation_method": "data_driven",
            "claims": [],
        },
    ]

    decisions.append(f"Data-driven fallback: {len(sections)} sections from condition schema")

    return {
        "protocol": {
            **protocol,
            "composed_sections": sections,
        },
        "_decisions": decisions,
    }
