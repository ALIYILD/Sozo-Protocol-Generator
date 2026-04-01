"""Condition Match Agent — infers target conditions from prompts and files."""
from __future__ import annotations
import logging
import re
from .base import BaseAgent, AgentResult
from .registry import register_agent

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

        # If conditions already specified, validate them
        if conditions_explicit:
            registry = get_registry()
            valid = [c for c in conditions_explicit if registry.exists(c)]
            unknown = [c for c in conditions_explicit if not registry.exists(c)]

            # For unknown conditions, check aliases
            onboarder = ConditionOnboarder()
            draft_conditions = []
            for unk in unknown:
                # Try alias resolution
                resolved = CONDITION_ALIASES.get(unk.lower())
                if resolved and registry.exists(resolved):
                    valid.append(resolved)
                else:
                    draft_conditions.append(unk)

            return AgentResult(
                success=True,
                output_data={
                    "validated_conditions": sorted(set(valid)),
                    "draft_conditions": draft_conditions,
                    "confidence": 1.0 if not draft_conditions else 0.5,
                    "source": "explicit",
                },
                warnings=[f"Unknown condition '{c}' — will be treated as draft" for c in draft_conditions],
            )

        # Infer from prompt
        if prompt:
            intent = parse_intent_rules(prompt)
            registry = get_registry()
            valid = [c for c in intent.conditions if registry.exists(c)]

            if intent.all_conditions:
                valid = registry.list_slugs()

            return AgentResult(
                success=bool(valid),
                output_data={
                    "validated_conditions": valid,
                    "draft_conditions": [],
                    "confidence": intent.confidence,
                    "source": "inferred_from_prompt",
                    "inferred_doc_types": intent.doc_types,
                    "inferred_tier": intent.tier,
                },
                warnings=[] if valid else ["Could not infer conditions from prompt"],
            )

        return AgentResult(
            success=False,
            error="No conditions specified and no prompt to infer from",
        )
