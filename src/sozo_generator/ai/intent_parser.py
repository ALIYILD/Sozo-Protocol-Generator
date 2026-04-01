"""
Intent parser — extracts structured actions from natural language.

Works in two modes:
1. LLM mode: Uses Claude/OpenAI to parse complex requests
2. Rule mode: Keyword matching fallback when no API key is set

SAFETY: This module ONLY parses intent. It never generates clinical content.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ── All known condition slugs and aliases ────────────────────────────────

CONDITION_ALIASES: dict[str, str] = {
    # Slug → slug (identity)
    "parkinsons": "parkinsons",
    "depression": "depression",
    "anxiety": "anxiety",
    "adhd": "adhd",
    "alzheimers": "alzheimers",
    "stroke_rehab": "stroke_rehab",
    "tbi": "tbi",
    "chronic_pain": "chronic_pain",
    "ptsd": "ptsd",
    "ocd": "ocd",
    "ms": "ms",
    "asd": "asd",
    "long_covid": "long_covid",
    "tinnitus": "tinnitus",
    "insomnia": "insomnia",
    # Common aliases
    "parkinson": "parkinsons",
    "parkinson's": "parkinsons",
    "parkinsons disease": "parkinsons",
    "pd": "parkinsons",
    "mdd": "depression",
    "major depression": "depression",
    "major depressive": "depression",
    "depressive disorder": "depression",
    "gad": "anxiety",
    "generalized anxiety": "anxiety",
    "anxiety disorder": "anxiety",
    "attention deficit": "adhd",
    "add": "adhd",
    "alzheimer": "alzheimers",
    "alzheimer's": "alzheimers",
    "mci": "alzheimers",
    "mild cognitive": "alzheimers",
    "dementia": "alzheimers",
    "stroke": "stroke_rehab",
    "post stroke": "stroke_rehab",
    "post-stroke": "stroke_rehab",
    "cerebrovascular": "stroke_rehab",
    "traumatic brain": "tbi",
    "brain injury": "tbi",
    "concussion": "tbi",
    "post-concussion": "tbi",
    "fibromyalgia": "chronic_pain",
    "chronic pain": "chronic_pain",
    "pain": "chronic_pain",
    "fibro": "chronic_pain",
    "post-traumatic stress": "ptsd",
    "post traumatic": "ptsd",
    "trauma": "ptsd",
    "obsessive": "ocd",
    "compulsive": "ocd",
    "multiple sclerosis": "ms",
    "autism": "asd",
    "autistic": "asd",
    "autism spectrum": "asd",
    "long covid": "long_covid",
    "post covid": "long_covid",
    "post-covid": "long_covid",
    "brain fog": "long_covid",
    "covid": "long_covid",
    "sleep": "insomnia",
    "sleep disorder": "insomnia",
}

DOC_TYPE_ALIASES: dict[str, str] = {
    "evidence based protocol": "evidence_based_protocol",
    "evidence-based protocol": "evidence_based_protocol",
    "evidence protocol": "evidence_based_protocol",
    "ebp": "evidence_based_protocol",
    "protocol": "evidence_based_protocol",
    "all in one": "all_in_one_protocol",
    "all-in-one": "all_in_one_protocol",
    "aio": "all_in_one_protocol",
    "handbook": "handbook",
    "clinical handbook": "handbook",
    "clinical exam": "clinical_exam",
    "examination": "clinical_exam",
    "exam checklist": "clinical_exam",
    "phenotype": "phenotype_classification",
    "phenotype classification": "phenotype_classification",
    "responder": "responder_tracking",
    "responder tracking": "responder_tracking",
    "tracking": "responder_tracking",
    "psych intake": "psych_intake",
    "psychological intake": "psych_intake",
    "intake": "psych_intake",
    "prs": "psych_intake",
    "network assessment": "network_assessment",
    "bedside assessment": "network_assessment",
    "6-network": "network_assessment",
    "fnon assessment": "network_assessment",
}

TIER_ALIASES: dict[str, str] = {
    "fellow": "fellow",
    "partners": "partners",
    "both": "both",
    "all tiers": "both",
    "partner": "partners",
}


@dataclass
class UserIntent:
    """Parsed user intent from natural language."""

    action: str = "unknown"  # generate, merge, list, explain, qa, upload, help
    conditions: list[str] = field(default_factory=list)  # condition slugs
    doc_types: list[str] = field(default_factory=list)  # doc type slugs
    tier: str = "both"
    all_conditions: bool = False
    merge_request: bool = False
    merge_doc_types: list[str] = field(default_factory=list)
    custom_title: Optional[str] = None
    sections_filter: list[str] = field(default_factory=list)
    template_path: Optional[str] = None
    raw_text: str = ""
    confidence: float = 1.0  # how confident the parser is

    @property
    def is_generation_request(self) -> bool:
        return self.action in ("generate", "merge", "upload")

    @property
    def summary(self) -> str:
        parts = [f"Action: {self.action}"]
        if self.all_conditions:
            parts.append("Conditions: ALL 15")
        elif self.conditions:
            parts.append(f"Conditions: {', '.join(self.conditions)}")
        if self.doc_types:
            parts.append(f"Doc types: {', '.join(self.doc_types)}")
        parts.append(f"Tier: {self.tier}")
        if self.merge_request:
            parts.append(f"Merge: {', '.join(self.merge_doc_types)}")
        return " | ".join(parts)


def parse_intent_rules(text: str) -> UserIntent:
    """
    Rule-based intent parser. Works without any LLM API key.
    Parses conditions, doc types, tiers, and actions from natural language.
    """
    text_lower = text.lower().strip()
    intent = UserIntent(raw_text=text)

    # ── Detect action ──
    if any(w in text_lower for w in ["merge", "combine", "join", "consolidate", "put together"]):
        intent.action = "merge"
        intent.merge_request = True
    elif any(w in text_lower for w in ["generate", "create", "build", "make", "produce", "give me", "i want", "i need", "prepare"]):
        intent.action = "generate"
    elif any(w in text_lower for w in ["list", "show", "what conditions", "what documents", "available"]):
        intent.action = "list"
    elif any(w in text_lower for w in ["explain", "what is", "tell me about", "describe"]):
        intent.action = "explain"
    elif any(w in text_lower for w in ["qa", "quality", "check", "validate", "review"]):
        intent.action = "qa"
    elif any(w in text_lower for w in ["upload", "uploaded"]):
        intent.action = "upload"
    elif any(w in text_lower for w in ["help", "how to", "how do"]):
        intent.action = "help"
    else:
        # Default to generate if conditions/docs mentioned
        intent.action = "generate"

    # ── Detect "all conditions" ──
    if any(p in text_lower for p in ["all conditions", "all 15", "every condition", "all of them", "everything"]):
        intent.all_conditions = True

    # ── Detect conditions ──
    found_conditions = set()
    # Sort aliases by length descending so longer matches win
    sorted_aliases = sorted(CONDITION_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
    remaining = text_lower
    for alias, slug in sorted_aliases:
        if alias in remaining:
            found_conditions.add(slug)
            # Don't remove from remaining — allow multiple matches
    intent.conditions = sorted(found_conditions)

    # ── Detect doc types ──
    found_docs = set()
    sorted_doc_aliases = sorted(DOC_TYPE_ALIASES.items(), key=lambda x: len(x[0]), reverse=True)
    for alias, doc_slug in sorted_doc_aliases:
        if alias in text_lower:
            found_docs.add(doc_slug)
            if intent.merge_request:
                intent.merge_doc_types.append(doc_slug)
    intent.doc_types = sorted(found_docs)

    # If "all documents" or no specific doc type for a generate request
    if any(p in text_lower for p in ["all documents", "all docs", "all 15 docs", "every document"]):
        intent.doc_types = []  # empty means "all"

    # ── Detect tier ──
    for alias, tier_slug in TIER_ALIASES.items():
        if alias in text_lower:
            intent.tier = tier_slug
            break

    # ── Detect custom title ──
    title_match = re.search(r'(?:title|called|named)\s*[:\"]?\s*(.+?)[\"\n]', text_lower)
    if title_match:
        intent.custom_title = title_match.group(1).strip().strip('"\'')

    # ── Confidence scoring ──
    if intent.action == "unknown":
        intent.confidence = 0.3
    elif not intent.conditions and not intent.all_conditions and intent.action == "generate":
        intent.confidence = 0.5
    else:
        intent.confidence = 0.9

    return intent


def parse_intent_llm(text: str, api_key: str, provider: str = "anthropic") -> UserIntent:
    """
    LLM-powered intent parser for complex/ambiguous requests.

    SAFETY: The LLM prompt explicitly instructs the model to ONLY parse intent,
    never generate clinical content.
    """
    system_prompt = """You are a clinical document management assistant for SOZO Brain Center.
Your ONLY job is to parse the user's request into a structured JSON intent.
You NEVER generate clinical content, PMIDs, treatment recommendations, or medical advice.

The system manages 15 neurological conditions:
parkinsons, depression, anxiety, adhd, alzheimers, stroke_rehab, tbi, chronic_pain, ptsd, ocd, ms, asd, long_covid, tinnitus, insomnia

And 8 document types:
evidence_based_protocol, all_in_one_protocol, handbook, clinical_exam, phenotype_classification, responder_tracking, psych_intake, network_assessment

Tiers: fellow, partners, both

Parse the user's request and return ONLY valid JSON:
{
  "action": "generate|merge|list|explain|qa|help",
  "conditions": ["slug1", "slug2"],
  "all_conditions": false,
  "doc_types": ["doc_type1"],
  "tier": "both",
  "merge_request": false,
  "merge_doc_types": [],
  "custom_title": null,
  "sections_filter": []
}"""

    try:
        if provider == "anthropic":
            return _call_anthropic(text, system_prompt, api_key)
        else:
            return _call_openai(text, system_prompt, api_key)
    except Exception as e:
        logger.warning("LLM intent parsing failed, falling back to rules: %s", e)
        return parse_intent_rules(text)


def _call_anthropic(text: str, system_prompt: str, api_key: str) -> UserIntent:
    """Call Anthropic Claude API for intent parsing."""
    import httpx

    response = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": text}],
        },
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()
    content = data["content"][0]["text"]

    # Extract JSON from response
    json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if json_match:
        parsed = json.loads(json_match.group())
        intent = UserIntent(
            action=parsed.get("action", "generate"),
            conditions=parsed.get("conditions", []),
            all_conditions=parsed.get("all_conditions", False),
            doc_types=parsed.get("doc_types", []),
            tier=parsed.get("tier", "both"),
            merge_request=parsed.get("merge_request", False),
            merge_doc_types=parsed.get("merge_doc_types", []),
            custom_title=parsed.get("custom_title"),
            sections_filter=parsed.get("sections_filter", []),
            raw_text=text,
            confidence=0.95,
        )
        return intent

    # Fallback
    return parse_intent_rules(text)


def _call_openai(text: str, system_prompt: str, api_key: str) -> UserIntent:
    """Call OpenAI API for intent parsing."""
    import httpx

    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            "max_tokens": 500,
            "temperature": 0,
        },
        timeout=15.0,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]

    json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
    if json_match:
        parsed = json.loads(json_match.group())
        return UserIntent(
            action=parsed.get("action", "generate"),
            conditions=parsed.get("conditions", []),
            all_conditions=parsed.get("all_conditions", False),
            doc_types=parsed.get("doc_types", []),
            tier=parsed.get("tier", "both"),
            merge_request=parsed.get("merge_request", False),
            merge_doc_types=parsed.get("merge_doc_types", []),
            custom_title=parsed.get("custom_title"),
            raw_text=text,
            confidence=0.95,
        )

    return parse_intent_rules(text)
