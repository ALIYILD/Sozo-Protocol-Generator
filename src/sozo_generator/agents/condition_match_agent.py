"""Condition Match Agent — infers target conditions from prompts and files.

Validates conditions against the registry, resolves aliases, flags unknowns
as drafts, and provides confidence scores with reviewer warnings.
"""
from __future__ import annotations
import logging
from .base import BaseAgent, AgentResult
from .registry import register_agent

logger = logging.getLogger(__name__)

# Confidence thresholds
_HIGH_CONFIDENCE = 0.8
_MEDIUM_CONFIDENCE = 0.5
_LOW_CONFIDENCE = 0.3


@register_agent
class ConditionMatchAgent(BaseAgent):
    name = "condition_match_agent"
    role = "Infer target conditions from prompts and uploaded files"

    def execute(self, input_data: dict, workspace_path: str, **kwargs) -> AgentResult:
        from ..ai.intent_parser import parse_intent_rules, CONDITION_ALIASES
        from ..conditions.registry import get_registry
        from ..conditions.onboarding import ConditionOnboarder

        prompt = input_data.get("prompt", "")
        conditions_explicit = input_data.get("conditions", [])
        warnings = []

        registry = get_registry()
        all_slugs = set(registry.list_slugs())

        # ── Path 1: Explicit conditions provided ──
        if conditions_explicit:
            valid = []
            draft_conditions = []

            for c in conditions_explicit:
                if c in all_slugs:
                    valid.append(c)
                else:
                    # Try alias resolution
                    resolved = CONDITION_ALIASES.get(c.lower())
                    if resolved and resolved in all_slugs:
                        valid.append(resolved)
                    else:
                        draft_conditions.append(c)
                        warnings.append(
                            f"Unknown condition '{c}' — will be treated as draft "
                            f"(requires clinical review before any output is usable)"
                        )

            confidence = 1.0 if not draft_conditions else 0.5
            return AgentResult(
                success=True,
                output_data={
                    "validated_conditions": sorted(set(valid)),
                    "draft_conditions": draft_conditions,
                    "all_conditions": False,
                    "confidence": confidence,
                    "source": "explicit",
                },
                warnings=warnings,
            )

        # ── Path 2: Infer from prompt ──
        if prompt:
            intent = parse_intent_rules(prompt)

            if intent.all_conditions:
                return AgentResult(
                    success=True,
                    output_data={
                        "validated_conditions": sorted(all_slugs),
                        "draft_conditions": [],
                        "all_conditions": True,
                        "confidence": 0.9,
                        "source": "inferred_all",
                        "inferred_doc_types": intent.doc_types,
                        "inferred_tier": intent.tier,
                    },
                )

            valid = [c for c in intent.conditions if c in all_slugs]

            # Check for unresolved condition words in the prompt
            # that the intent parser might have found but aren't valid slugs
            unresolved = [c for c in intent.conditions if c not in all_slugs]
            draft_conditions = []
            for u in unresolved:
                resolved = CONDITION_ALIASES.get(u.lower())
                if resolved and resolved in all_slugs and resolved not in valid:
                    valid.append(resolved)
                elif u not in valid:
                    draft_conditions.append(u)
                    warnings.append(
                        f"Unrecognized condition '{u}' in prompt — treating as draft"
                    )

            # Confidence scoring
            if valid and not draft_conditions:
                confidence = _HIGH_CONFIDENCE if len(valid) <= 3 else 0.85
            elif valid and draft_conditions:
                confidence = _MEDIUM_CONFIDENCE
            elif not valid and intent.action in ("generate", "merge"):
                confidence = _LOW_CONFIDENCE
                warnings.append(
                    "No specific condition detected in prompt. "
                    "Please select conditions manually or be more specific."
                )
            else:
                confidence = intent.confidence

            return AgentResult(
                success=bool(valid),
                output_data={
                    "validated_conditions": sorted(set(valid)),
                    "draft_conditions": draft_conditions,
                    "all_conditions": False,
                    "confidence": confidence,
                    "source": "inferred_from_prompt",
                    "inferred_doc_types": intent.doc_types,
                    "inferred_tier": intent.tier,
                },
                warnings=warnings,
            )

        # ── Path 3: Nothing provided ──
        return AgentResult(
            success=False,
            error="No conditions specified and no prompt to infer from",
            warnings=["Provide conditions explicitly or write a prompt describing what you need"],
        )
