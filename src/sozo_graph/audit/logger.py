"""
Node-level audit logging decorator.

Every node in the Sozo graph is wrapped with @audited_node to:
1. Record start/end timestamps and duration
2. Hash inputs and outputs for integrity verification
3. Capture decisions made by the node
4. Handle errors gracefully and record them in state
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


def audited_node(node_id: str):
    """Decorator that wraps a LangGraph node function with audit logging.

    The wrapped function must accept a state dict and return a partial state update dict.
    The decorator adds node_history entries and error entries to the returned dict.

    Usage:
        @audited_node("evidence_search")
        def evidence_search(state: SozoGraphState) -> dict:
            ...
            return {"evidence": {...}, "_decisions": ["Searched PubMed: 42 results"]}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(state: dict) -> dict:
            start = time.monotonic()
            started_at = datetime.now(timezone.utc).isoformat()

            # Hash inputs (exclude large/binary fields and history)
            input_hash = _hash_state(state)

            try:
                result = func(state)
                if not isinstance(result, dict):
                    result = {}

                completed_at = datetime.now(timezone.utc).isoformat()
                duration_ms = (time.monotonic() - start) * 1000
                output_hash = _hash_state(result)

                # Extract decisions from result (node puts them in _decisions)
                decisions = result.pop("_decisions", [])

                # Build history entry
                entry = {
                    "node_id": node_id,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "duration_ms": round(duration_ms, 2),
                    "status": "success",
                    "error": None,
                    "input_hash": input_hash,
                    "output_hash": output_hash,
                    "decisions": decisions,
                }

                # Append to node_history (uses operator.add reducer)
                result.setdefault("node_history", []).append(entry)
                result["updated_at"] = completed_at

                logger.info(
                    "Node %s completed in %.1fms (%d decisions)",
                    node_id, duration_ms, len(decisions),
                )
                return result

            except Exception as e:
                completed_at = datetime.now(timezone.utc).isoformat()
                duration_ms = (time.monotonic() - start) * 1000

                logger.error("Node %s failed: %s", node_id, e, exc_info=True)

                error_entry = {
                    "node_id": node_id,
                    "error_type": type(e).__name__,
                    "message": str(e)[:500],
                    "recoverable": True,
                    "timestamp": completed_at,
                }

                history_entry = {
                    "node_id": node_id,
                    "started_at": started_at,
                    "completed_at": completed_at,
                    "duration_ms": round(duration_ms, 2),
                    "status": "error",
                    "error": str(e)[:200],
                    "input_hash": input_hash,
                    "output_hash": "",
                    "decisions": [],
                }

                return {
                    "node_history": [history_entry],
                    "errors": [error_entry],
                    "updated_at": completed_at,
                    "status": "error",
                }

        return wrapper
    return decorator


def _hash_state(state: dict) -> str:
    """Compute a short SHA-256 hash of the state dict for integrity tracking.

    Skips binary fields and large lists to keep hashing fast.
    """
    # Only hash serializable, non-binary fields
    filtered = {}
    for k, v in state.items():
        if k in ("node_history", "errors", "uploaded_file", "eeg_file"):
            continue
        if isinstance(v, bytes):
            continue
        filtered[k] = v

    try:
        payload = json.dumps(filtered, sort_keys=True, default=str)
        return hashlib.sha256(payload.encode()).hexdigest()[:16]
    except (TypeError, ValueError):
        return "unhashable"
