"""
condition_resolver — validates condition slug against registry and loads full schema.

Type: Deterministic
"""
from __future__ import annotations

import logging

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("condition_resolver")
def condition_resolver(state: SozoGraphState) -> dict:
    """Resolve condition slug to a full ConditionSchema from the registry."""
    decisions = []

    # Determine slug from intake (prompt-normalized or template-inferred)
    intake = state.get("intake", {})
    normalized = intake.get("normalized_request") or {}
    template = intake.get("template_profile") or {}

    slug = (
        normalized.get("condition_slug")
        or template.get("inferred_condition")
        or state.get("condition", {}).get("slug")
    )

    if not slug:
        decisions.append("No condition slug found in intake — condition_valid=false")
        return {
            "condition": {
                "slug": "",
                "display_name": "",
                "icd10": "",
                "schema_dict": {},
                "resolution_source": "none",
                "condition_valid": False,
            },
            "_decisions": decisions,
        }

    # Load from registry
    try:
        from sozo_generator.conditions.registry import get_registry
        registry = get_registry()

        if not registry.exists(slug):
            decisions.append(f"Condition '{slug}' not found in registry")
            return {
                "condition": {
                    "slug": slug,
                    "display_name": "",
                    "icd10": "",
                    "schema_dict": {},
                    "resolution_source": "registry_miss",
                    "condition_valid": False,
                },
                "_decisions": decisions,
            }

        schema = registry.get(slug)
        source = "registry"
        if normalized.get("condition_slug"):
            source = "prompt_inferred"
        elif template.get("inferred_condition"):
            source = "template_inferred"

        decisions.append(f"Resolved '{slug}' → {schema.display_name} (ICD-10: {schema.icd10}) via {source}")

        return {
            "condition": {
                "slug": schema.slug,
                "display_name": schema.display_name,
                "icd10": schema.icd10,
                "schema_dict": schema.model_dump(),
                "resolution_source": source,
                "condition_valid": True,
            },
            "status": "intake",
            "_decisions": decisions,
        }

    except Exception as e:
        logger.error("Condition resolution failed: %s", e)
        decisions.append(f"Registry error: {e}")
        return {
            "condition": {
                "slug": slug,
                "display_name": "",
                "icd10": "",
                "schema_dict": {},
                "resolution_source": "error",
                "condition_valid": False,
            },
            "_decisions": decisions,
        }
