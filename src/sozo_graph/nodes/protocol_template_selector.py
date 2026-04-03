"""
protocol_template_selector — selects base protocol template and builds SOZO sequence.

Type: Deterministic
Wraps: sozo_protocol.builder.build_sozo_sequence
"""
from __future__ import annotations

import logging

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("protocol_template_selector")
def protocol_template_selector(state: SozoGraphState) -> dict:
    """Select the protocol template and build the base SOZO sequence."""
    decisions = []
    condition = state.get("condition", {})
    slug = condition.get("slug", "")
    tier = state.get("protocol", {}).get("tier", "fellow")

    try:
        from sozo_protocol.builder import build_sozo_sequence

        # Try knowledge-based build first
        kb_protocols = None
        try:
            from sozo_generator.knowledge.base import KnowledgeBase
            kb = KnowledgeBase()
            kb.load_all()
            cond = kb.get_condition(slug)
            if cond and cond.protocols:
                kb_protocols = [p.__dict__ if hasattr(p, '__dict__') else p for p in cond.protocols]
                decisions.append(f"Loaded {len(kb_protocols)} protocols from knowledge base")
        except Exception as e:
            logger.debug("Knowledge base not available: %s", e)

        sequence = build_sozo_sequence(
            condition_slug=slug,
            tier=tier,
            knowledge_protocols=kb_protocols,
        )

        decisions.append(
            f"Built SOZO sequence: {sequence.name}, "
            f"{len(sequence.phases)} phases, "
            f"modalities: {list(sequence.all_modalities)}, "
            f"duration: {sequence.total_duration_min:.0f} min"
        )

        return {
            "protocol": {
                "base_sequence": sequence.model_dump(),
                "template_source": "knowledge_base" if kb_protocols else "default_builder",
                "selection_rationale": f"Standard SOZO sequence for {condition.get('display_name', slug)}",
                "doc_type": "evidence_based_protocol",
                "tier": tier,
            },
            "_decisions": decisions,
        }

    except Exception as e:
        logger.error("Protocol template selection failed: %s", e)
        decisions.append(f"Template selection error: {e}")
        return {
            "protocol": {
                "base_sequence": {},
                "template_source": "error",
                "selection_rationale": str(e),
            },
            "_decisions": decisions,
        }
