"""
audit_logger — writes complete execution audit record.

Type: Deterministic
CRITICAL: If audit write fails, release is BLOCKED.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from ..audit.logger import audited_node
from ..state import SozoGraphState

logger = logging.getLogger(__name__)


@audited_node("audit_logger")
def audit_logger(state: SozoGraphState) -> dict:
    """Write the complete audit record for this protocol generation run."""
    decisions = []

    from sozo_generator.core.settings import get_settings
    settings = get_settings()

    condition = state.get("condition", {})
    evidence = state.get("evidence", {})
    safety = state.get("safety", {})
    review = state.get("review", {})
    node_history = state.get("node_history", [])

    # Build audit record
    audit_id = f"audit-{state.get('request_id', 'unknown')}"
    now = datetime.now(timezone.utc).isoformat()

    # Compute stats
    total_nodes = len(node_history)
    llm_calls = sum(1 for n in node_history if n.get("node_id") in (
        "prompt_normalizer", "protocol_composer", "eeg_interpreter",
    ))
    total_duration = sum(n.get("duration_ms", 0) for n in node_history)

    # Evidence stats
    articles = evidence.get("articles", [])
    cited_ids = set()
    for section in state.get("protocol", {}).get("composed_sections", []):
        cited_ids.update(section.get("cited_evidence_ids", []))

    grade_dist = evidence.get("evidence_summary", {}).get("grade_distribution", {})

    audit_record = {
        "audit_id": audit_id,
        "request_id": state.get("request_id"),
        "condition_slug": condition.get("slug"),
        "condition_name": condition.get("display_name"),
        "created_at": state.get("created_at"),
        "completed_at": now,
        "total_duration_ms": round(total_duration, 2),

        # Execution trace
        "node_history": node_history,
        "errors": state.get("errors", []),
        "total_nodes_executed": total_nodes,
        "total_llm_calls": llm_calls,

        # Evidence audit
        "evidence_articles_searched": evidence.get("raw_article_count", 0),
        "evidence_articles_screened": evidence.get("screened_article_count", 0),
        "evidence_articles_cited": len(cited_ids),
        "evidence_ids_cited": sorted(cited_ids),
        "evidence_grade_distribution": grade_dist,
        "prisma_counts": evidence.get("prisma_counts", {}),

        # Safety audit
        "contraindications_checked": [
            c.get("contraindication", "") for c in safety.get("contraindications_found", [])
        ],
        "safety_flags_raised": safety.get("blocking_contraindications", []),
        "consent_requirements": safety.get("consent_requirements", []),

        # Review audit
        "review_cycles": review.get("revision_number", 0),
        "reviewer_id": review.get("reviewer_id"),
        "review_decision": review.get("status"),
        "approval_stamp": review.get("approval_stamp"),

        # Output
        "output_paths": state.get("output", {}).get("output_paths", {}),
        "graph_version": state.get("graph_version"),
        "state_version": state.get("version"),
    }

    # Persist audit record
    audit_dir = settings.output_dir / "audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    audit_path = audit_dir / f"{audit_id}.json"

    try:
        audit_path.write_text(json.dumps(audit_record, indent=2, default=str))
        decisions.append(f"Audit record written: {audit_path} ({total_nodes} nodes, {len(cited_ids)} citations)")
    except Exception as e:
        # AUDIT FAILURE BLOCKS RELEASE
        logger.error("CRITICAL: Audit write failed: %s", e)
        decisions.append(f"CRITICAL: Audit write failed: {e}")
        return {
            "status": "error",
            "errors": [{
                "node_id": "audit_logger",
                "error_type": "AuditWriteFailure",
                "message": f"Audit write blocked release: {e}",
                "recoverable": True,
                "timestamp": now,
            }],
            "_decisions": decisions,
        }

    return {
        "output": {
            **state.get("output", {}),
            "audit_record_id": audit_id,
        },
        "_decisions": decisions,
    }
