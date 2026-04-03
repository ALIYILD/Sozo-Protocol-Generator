"""
eeg_interpreter — LLM node that interprets EEG features in clinical context.

Type: LLM node (structured output)
Identifies relevant biomarkers, network dysfunction patterns, and
recommends protocol adjustments grounded in evidence.
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


class EEGFinding(BaseModel):
    finding: str
    biomarker: str
    clinical_relevance: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: str = "medium"


class ParameterAdjustment(BaseModel):
    parameter: str  # intensity, target, frequency, duration
    current_value: str
    recommended_value: str
    rationale: str
    evidence_ids: list[str] = Field(default_factory=list)
    confidence: str = "medium"
    uncertainty_flag: Optional[str] = None


class EEGInterpretation(BaseModel):
    primary_findings: list[EEGFinding] = Field(default_factory=list)
    recommended_adjustments: list[ParameterAdjustment] = Field(default_factory=list)
    confidence: str = "medium"
    interpretation_notes: str = ""
    evidence_ids: list[str] = Field(default_factory=list)


# ── System prompt ──────────────────────────────────────────────────────

EEG_INTERPRETER_SYSTEM_PROMPT = """You are Sozo's EEG interpretation engine. You analyze quantitative EEG features in the context of a specific neurological/psychiatric condition and recommend protocol parameter adjustments.

CRITICAL RULES:
1. Every finding MUST cite evidence_ids from the literature. Do NOT fabricate PMIDs.
2. Every recommended adjustment MUST include a rationale and evidence_ids.
3. If confidence in an adjustment is low, set uncertainty_flag with an explanation.
4. You recommend adjustments — you do NOT apply them. A deterministic personalizer will apply them within safety bounds.
5. Never recommend parameters outside the modality's safety envelope.
6. Return ONLY valid JSON matching the output schema.

Known biomarker-condition associations:
- Depression: frontal alpha asymmetry (L<R), elevated theta/beta ratio, reduced alpha power
- Parkinson's: excessive beta power in motor cortex, reduced alpha in posterior regions
- ADHD: elevated theta/beta ratio, reduced beta in frontal regions
- Anxiety: elevated beta power, reduced alpha
- Insomnia: elevated beta at bedtime, reduced delta/theta in sleep onset

OUTPUT FORMAT:
{
  "primary_findings": [
    {"finding": "...", "biomarker": "...", "clinical_relevance": "...", "evidence_ids": ["..."], "confidence": "high|medium|low"}
  ],
  "recommended_adjustments": [
    {"parameter": "target|intensity|frequency|duration", "current_value": "...", "recommended_value": "...", "rationale": "...", "evidence_ids": ["..."], "confidence": "high|medium|low", "uncertainty_flag": null}
  ],
  "confidence": "high|medium|low",
  "interpretation_notes": "...",
  "evidence_ids": ["..."]
}"""


@audited_node("eeg_interpreter")
def eeg_interpreter(state: SozoGraphState) -> dict:
    """Interpret EEG features and recommend protocol adjustments."""
    decisions = []
    eeg = state.get("eeg") or {}
    condition = state.get("condition", {})
    evidence = state.get("evidence", {})

    features = eeg.get("features", {})
    quality = eeg.get("quality_metrics", {})

    if not features or not quality.get("usable", False):
        decisions.append("EEG features not usable — skipping interpretation")
        return {
            "eeg": {
                **eeg,
                "interpretation": EEGInterpretation(
                    interpretation_notes="No usable EEG features available",
                    confidence="insufficient",
                ).model_dump(),
            },
            "_decisions": decisions,
        }

    # Try LLM interpretation
    try:
        from sozo_generator.core.settings import get_settings
        settings = get_settings()

        if not settings.anthropic_api_key:
            decisions.append("No API key — using rule-based EEG interpretation")
            interpretation = _rule_based_interpret(features, condition, evidence)
        else:
            interpretation = _llm_interpret(features, condition, evidence, settings.anthropic_api_key)
            decisions.append(f"LLM interpreted: {len(interpretation.primary_findings)} findings, "
                           f"{len(interpretation.recommended_adjustments)} adjustments")

    except Exception as e:
        logger.error("EEG interpretation failed: %s", e)
        decisions.append(f"LLM interpretation failed: {e} — falling back to rule-based")
        interpretation = _rule_based_interpret(features, condition, evidence)

    return {
        "eeg": {
            **eeg,
            "interpretation": interpretation.model_dump(),
        },
        "_decisions": decisions,
    }


def _llm_interpret(
    features: dict, condition: dict, evidence: dict, api_key: str,
) -> EEGInterpretation:
    """LLM-based EEG interpretation."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    # Build evidence context
    evidence_context = []
    for a in evidence.get("articles", [])[:10]:
        evidence_context.append({
            "id": a.get("pmid") or a.get("doi", ""),
            "title": a.get("title", ""),
            "year": a.get("year"),
        })

    user_message = json.dumps({
        "condition_slug": condition.get("slug"),
        "condition_name": condition.get("display_name"),
        "eeg_features": features,
        "available_evidence": evidence_context,
    }, default=str)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=EEG_INTERPRETER_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = response.content[0].text
    parsed = json.loads(raw)
    return EEGInterpretation.model_validate(parsed)


def _rule_based_interpret(
    features: dict, condition: dict, evidence: dict,
) -> EEGInterpretation:
    """Rule-based EEG interpretation fallback."""
    findings = []
    adjustments = []
    slug = condition.get("slug", "")

    # Check frontal alpha asymmetry (depression biomarker)
    alpha_asym = features.get("frontal_alpha_asymmetry") or features.get("alpha_asymmetry_f3_f4")
    if alpha_asym is not None and slug in ("depression", "anxiety"):
        if alpha_asym < -0.1:  # left < right
            findings.append(EEGFinding(
                finding="Reduced left frontal alpha power relative to right",
                biomarker="frontal_alpha_asymmetry",
                clinical_relevance="Associated with approach motivation deficit in depression",
                confidence="medium",
            ))
            adjustments.append(ParameterAdjustment(
                parameter="target",
                current_value="left DLPFC",
                recommended_value="left DLPFC (confirmed by EEG)",
                rationale="Left frontal hypoactivation confirmed by alpha asymmetry — standard tDCS target appropriate",
                confidence="medium",
            ))

    # Check theta/beta ratio (ADHD biomarker)
    tbr = features.get("theta_beta_ratio") or features.get("tbr")
    if tbr is not None and slug in ("adhd",):
        if tbr > 4.5:
            findings.append(EEGFinding(
                finding=f"Elevated theta/beta ratio ({tbr:.1f})",
                biomarker="theta_beta_ratio",
                clinical_relevance="Consistent with ADHD cortical underarousal pattern",
                confidence="medium",
            ))

    # Check beta power (motor cortex - Parkinson's)
    beta_c3 = features.get("beta_power_c3") or features.get("beta_c3")
    if beta_c3 is not None and slug in ("parkinsons",):
        if beta_c3 > 15.0:  # arbitrary threshold
            findings.append(EEGFinding(
                finding=f"Elevated beta power at C3 ({beta_c3:.1f} µV²)",
                biomarker="motor_beta",
                clinical_relevance="Excessive beta synchronization in motor cortex consistent with parkinsonian bradykinesia",
                confidence="medium",
            ))

    return EEGInterpretation(
        primary_findings=findings,
        recommended_adjustments=adjustments,
        confidence="medium" if findings else "low",
        interpretation_notes=f"Rule-based interpretation for {slug}: {len(findings)} findings",
    )
