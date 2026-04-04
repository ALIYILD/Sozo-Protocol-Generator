"""
condition_resolver — validates condition slug against registry and loads full schema.

Type: Deterministic

Slug precedence matches ``unified_graph.condition_resolver_node``:
explicit ``intake.condition_slug`` → ``normalized_request.condition_slug`` →
template ``inferred_condition`` → ``state.condition.slug`` → prompt heuristic.
"""
from __future__ import annotations

import logging
from typing import Optional

from .. import integration
from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("condition_resolver")
def condition_resolver(state: SozoGraphState) -> dict:
    """Resolve condition slug to a full ConditionSchema from the registry."""
    decisions = []
    intake = dict(state.get("intake") or {})
    normalized = dict(intake.get("normalized_request") or {})
    template = intake.get("template_profile") or {}

    explicit = (intake.get("condition_slug") or "").strip() or None
    norm_slug = (normalized.get("condition_slug") or "").strip() or None

    warnings = list(intake.get("parse_warnings") or [])

    if explicit and norm_slug and explicit != norm_slug:
        msg = (
            f"intake_condition_slug_mismatch: explicit={explicit!r} "
            f"normalized_request={norm_slug!r}"
        )
        warnings.append(msg)
        decisions.append(msg)

    chosen_slug: Optional[str] = None
    slug_source = "none"

    if explicit:
        chosen_slug = explicit
        slug_source = "explicit_intake"
    elif norm_slug:
        chosen_slug = norm_slug
        slug_source = "normalized_request"
    else:
        t_slug = (template.get("inferred_condition") or "").strip() or None
        if t_slug:
            chosen_slug = t_slug
            slug_source = "template_inferred"

    if not chosen_slug:
        carried = (state.get("condition") or {}).get("slug")
        if carried:
            chosen_slug = str(carried).strip() or None
            slug_source = "state_carryover"

    inferred_prompt = integration.infer_condition_slug_from_prompt(
        intake.get("user_prompt")
    )

    intake_conflict = False
    intake_conflict_note: Optional[str] = None
    if (
        chosen_slug
        and inferred_prompt
        and inferred_prompt != chosen_slug
    ):
        res_struct = integration.resolve_condition(chosen_slug)
        res_inf = integration.resolve_condition(inferred_prompt)
        if res_struct.get("condition_valid") and res_inf.get("condition_valid"):
            intake_conflict = True
            intake_conflict_note = (
                f"prompt suggests {inferred_prompt!r} but structured "
                f"intake used {chosen_slug!r}"
            )
            warnings.append(f"condition_intake_conflict: {intake_conflict_note}")
            decisions.append(intake_conflict_note)

    if not chosen_slug and inferred_prompt:
        chosen_slug = inferred_prompt
        slug_source = "prompt_inferred"
        decisions.append(
            f"No structured condition slug; inferred {chosen_slug!r} from prompt"
        )

    if not chosen_slug:
        decisions.append("No condition slug found in intake — condition_valid=false")
        intake["parse_warnings"] = warnings
        return {
            "intake": intake,
            "condition": {
                "slug": "",
                "display_name": "",
                "icd10": "",
                "schema_dict": {},
                "resolution_source": "none",
                "condition_valid": False,
            },
            "status": "intake",
            "_decisions": decisions,
        }

    try:
        condition_data = integration.resolve_condition(chosen_slug)
    except Exception as e:
        logger.error("Condition resolution failed: %s", e)
        decisions.append(f"Registry error: {e}")
        intake["parse_warnings"] = warnings
        return {
            "intake": intake,
            "condition": {
                "slug": chosen_slug or "",
                "display_name": "",
                "icd10": "",
                "schema_dict": {},
                "resolution_source": "error",
                "condition_valid": False,
            },
            "status": "intake",
            "_decisions": decisions,
        }

    if intake_conflict and condition_data.get("condition_valid"):
        condition_data["intake_conflict"] = True
        if intake_conflict_note:
            condition_data["intake_conflict_note"] = intake_conflict_note

    if condition_data["condition_valid"] and slug_source != "none":
        condition_data["resolution_source"] = slug_source

    decisions.append(
        f"Resolved '{chosen_slug}' → {condition_data.get('display_name', '')} "
        f"(ICD-10: {condition_data.get('icd10', '')}) "
        f"via {condition_data.get('resolution_source', '')} "
        f"[valid={condition_data.get('condition_valid')}]"
    )

    intake["parse_warnings"] = warnings
    return {
        "condition": condition_data,
        "intake": intake,
        "status": "intake",
        "_decisions": decisions,
    }
