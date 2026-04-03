"""
prompt_normalizer — LLM node that interprets natural-language prompts
into structured request fields.

Type: LLM node (structured output)
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

class PatientContext(BaseModel):
    age: Optional[int] = None
    sex: Optional[str] = None
    diagnosis: Optional[str] = None
    symptoms: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    prior_neuromodulation: list[str] = Field(default_factory=list)
    severity: Optional[str] = None


class NormalizedRequest(BaseModel):
    condition_slug: str
    condition_display: str
    modality_preferences: list[str] = Field(default_factory=list)
    patient_context: Optional[PatientContext] = None
    personalization_requested: bool = False
    eeg_data_referenced: bool = False
    uncertainty_flags: list[str] = Field(default_factory=list)
    raw_prompt: str = ""


# ── System prompt ──────────────────────────────────────────────────────

NORMALIZER_SYSTEM_PROMPT = """You are Sozo's intake interpreter for a neuromodulation protocol generation system.

Your job is to interpret a clinician's natural-language request and extract structured fields.
You MUST return valid JSON matching the schema exactly. No prose outside the JSON.

Rules:
- condition_slug MUST be one of the provided available_conditions list. If unsure, pick the closest match and add an uncertainty_flag.
- modality_preferences MUST only include items from available_modalities: ["tdcs", "tps", "tavns", "ces"]
- If the prompt mentions EEG, QEEG, or brainwave data, set eeg_data_referenced: true.
- If the prompt mentions patient-specific factors (age, symptoms, prior treatment), set personalization_requested: true and populate patient_context.
- If you cannot confidently determine any field, set it to null and add a description to uncertainty_flags.
- NEVER fabricate clinical details not present in the prompt.
- NEVER recommend specific treatment parameters — that is not your role.

OUTPUT FORMAT:
{
  "condition_slug": "one of the available_conditions",
  "condition_display": "Human readable name",
  "modality_preferences": ["tdcs"],
  "patient_context": null or {"age": 55, "symptoms": ["tremor"]},
  "personalization_requested": false,
  "eeg_data_referenced": false,
  "uncertainty_flags": [],
  "raw_prompt": "echo the original prompt"
}"""

# Available conditions (loaded from registry at runtime)
AVAILABLE_CONDITIONS = [
    "parkinsons", "depression", "anxiety", "adhd", "alzheimers",
    "stroke_rehab", "tbi", "chronic_pain", "ptsd", "ocd",
    "ms", "asd", "long_covid", "tinnitus", "insomnia",
]


@audited_node("prompt_normalizer")
def prompt_normalizer(state: SozoGraphState) -> dict:
    """Interpret natural-language prompt into structured request."""
    decisions = []
    intake = state.get("intake", {})
    prompt = intake.get("user_prompt", "")

    if not prompt:
        decisions.append("Empty prompt — returning empty normalized request")
        return {
            "intake": {
                **intake,
                "normalized_request": NormalizedRequest(
                    condition_slug="",
                    condition_display="",
                    uncertainty_flags=["No prompt provided"],
                    raw_prompt="",
                ).model_dump(),
            },
            "_decisions": decisions,
        }

    user_message = json.dumps({
        "user_prompt": prompt,
        "available_conditions": AVAILABLE_CONDITIONS,
        "available_modalities": ["tdcs", "tps", "tavns", "ces"],
    })

    try:
        from sozo_generator.core.settings import get_settings
        settings = get_settings()

        if not settings.anthropic_api_key:
            # Fallback: keyword-based parsing
            decisions.append("No API key — using keyword-based normalization")
            normalized = _keyword_normalize(prompt)
            return {
                "intake": {**intake, "normalized_request": normalized.model_dump()},
                "_decisions": decisions,
            }

        import anthropic
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=NORMALIZER_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text = response.content[0].text
        parsed = json.loads(raw_text)
        normalized = NormalizedRequest.model_validate(parsed)
        normalized.raw_prompt = prompt

        decisions.append(
            f"Normalized: condition={normalized.condition_slug}, "
            f"modalities={normalized.modality_preferences}, "
            f"personalization={normalized.personalization_requested}, "
            f"uncertainties={len(normalized.uncertainty_flags)}"
        )

        return {
            "intake": {**intake, "normalized_request": normalized.model_dump()},
            "_decisions": decisions,
        }

    except Exception as e:
        logger.error("Prompt normalization failed: %s", e)
        decisions.append(f"LLM normalization failed: {e} — falling back to keywords")
        normalized = _keyword_normalize(prompt)
        return {
            "intake": {**intake, "normalized_request": normalized.model_dump()},
            "_decisions": decisions,
        }


def _keyword_normalize(prompt: str) -> NormalizedRequest:
    """Fallback keyword-based prompt normalization."""
    prompt_lower = prompt.lower()

    # Match condition (including common aliases)
    _ALIASES = {
        "parkinsons": ["parkinson", "parkinson's", "parkinsons"],
        "alzheimers": ["alzheimer", "alzheimer's", "alzheimers"],
        "stroke_rehab": ["stroke", "stroke rehab", "stroke rehabilitation"],
        "chronic_pain": ["chronic pain", "pain"],
        "long_covid": ["long covid", "post-covid", "post covid"],
    }
    condition_slug = ""
    condition_display = ""
    for slug in AVAILABLE_CONDITIONS:
        readable = slug.replace("_", " ")
        aliases = _ALIASES.get(slug, []) + [readable, slug]
        if any(alias in prompt_lower for alias in aliases):
            condition_slug = slug
            condition_display = readable.title()
            break

    # Match modality
    modalities = []
    mod_map = {"tdcs": "tdcs", "tps": "tps", "tavns": "tavns", "ces": "ces",
               "transcranial direct current": "tdcs", "transcranial pulse": "tps",
               "vagus nerve": "tavns", "cranial electrotherapy": "ces"}
    for keyword, mod in mod_map.items():
        if keyword in prompt_lower and mod not in modalities:
            modalities.append(mod)

    eeg = any(kw in prompt_lower for kw in ["eeg", "qeeg", "brainwave", "brain wave"])

    uncertainties = []
    if not condition_slug:
        uncertainties.append("Could not determine condition from prompt")

    return NormalizedRequest(
        condition_slug=condition_slug,
        condition_display=condition_display,
        modality_preferences=modalities,
        personalization_requested=False,
        eeg_data_referenced=eeg,
        uncertainty_flags=uncertainties,
        raw_prompt=prompt,
    )
