"""Audit event creation service.

Used by all other modules to create audit events. This is the write side
of the audit system -- append-only, never update or delete.

Now backed by a real SQLite database (audit_log table).
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AuditService:
    """Append-only audit event service backed by SQLite.

    All writes go through ``log_event``. The store is intentionally
    insert-only -- there are no update or delete methods, which is a
    hard requirement for clinical governance and regulatory compliance.
    """

    def _get_db(self) -> sqlite3.Connection:
        from sozo_api.routes.db_helper import get_db
        return get_db()

    # -- Core write method -------------------------------------------------------

    def log_event(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: Optional[str] = None,
        node_name: Optional[str] = None,
        details: Optional[dict] = None,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
    ) -> int:
        """Create an immutable audit event in SQLite.

        Computes SHA-256 hashes of input/output for integrity verification.
        Returns the auto-incremented event ID.
        """
        conn = self._get_db()
        try:
            cursor = conn.execute(
                "INSERT INTO audit_log "
                "(entity_type, entity_id, action, actor_id, node_name, "
                "input_hash, output_hash, details) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (
                    entity_type,
                    str(entity_id),
                    action,
                    actor or "system",
                    node_name,
                    self._hash(input_data) if input_data else None,
                    self._hash(output_data) if output_data else None,
                    json.dumps(details or {}, default=str),
                ),
            )
            conn.commit()
            event_id = cursor.lastrowid
        finally:
            conn.close()

        logger.info(
            "audit | %s %s/%s by %s (id=%d)",
            action, entity_type, entity_id, actor or "system", event_id,
        )
        return event_id

    # -- Convenience wrappers for common actions ---------------------------------

    def log_protocol_created(
        self,
        protocol_id: str,
        actor: str,
        condition: str,
        doc_type: str,
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="created",
            actor=actor,
            details={"condition": condition, "doc_type": doc_type},
        )

    def log_generation_started(
        self,
        protocol_id: str,
        build_id: str,
        generation_method: str = "langgraph_v2",
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="generation_started",
            details={"build_id": build_id, "generation_method": generation_method},
        )

    def log_generation_completed(
        self,
        protocol_id: str,
        build_id: str,
        sections_generated: int,
        evidence_count: int,
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="generation_completed",
            details={
                "build_id": build_id,
                "sections_generated": sections_generated,
                "evidence_count": evidence_count,
            },
        )

    def log_generation_failed(
        self,
        protocol_id: str,
        build_id: str,
        error: str,
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="generation_failed",
            details={"build_id": build_id, "error": error},
        )

    def log_review(
        self,
        protocol_id: str,
        review_id: str,
        actor: str,
        score: float,
        comments: str = "",
    ) -> int:
        return self.log_event(
            entity_type="review",
            entity_id=review_id,
            action="reviewed",
            actor=actor,
            details={
                "protocol_id": protocol_id,
                "score": score,
                "comments": comments,
            },
        )

    def log_approval(
        self,
        protocol_id: str,
        actor: str,
        review_id: str,
        approval_level: str = "clinical_lead",
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="approved",
            actor=actor,
            details={"review_id": review_id, "approval_level": approval_level},
        )

    def log_rejection(
        self,
        protocol_id: str,
        actor: str,
        review_id: str,
        reason: str,
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="rejected",
            actor=actor,
            details={"review_id": review_id, "reason": reason},
        )

    def log_node_execution(
        self,
        protocol_id: str,
        build_id: str,
        node_name: str,
        duration_ms: int,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
        decision: Optional[str] = None,
        node_status: str = "success",
    ) -> int:
        return self.log_event(
            entity_type="protocol",
            entity_id=protocol_id,
            action="node_executed",
            node_name=node_name,
            input_data=input_data,
            output_data=output_data,
            details={
                "build_id": build_id,
                "duration_ms": duration_ms,
                "decision": decision,
                "status": node_status,
            },
        )

    # -- Read helpers (used by audit routes) -------------------------------------

    def query_events(
        self,
        *,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        action: Optional[str] = None,
        actor: Optional[str] = None,
        node_name: Optional[str] = None,
        thread_id: Optional[str] = None,
        build_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        """Query audit_log with filters. Returns (rows, total_count).

        ``thread_id`` matches ``details.thread_id`` (JSON) or ``entity_id`` (e.g. graph runs).
        ``build_id`` matches ``details.build_id`` (JSON).
        """
        conn = self._get_db()
        try:
            where_clauses: list[str] = []
            params: list[Any] = []

            if entity_type:
                where_clauses.append("entity_type = ?")
                params.append(entity_type)
            if entity_id:
                where_clauses.append("entity_id = ?")
                params.append(entity_id)
            if action:
                where_clauses.append("action = ?")
                params.append(action)
            if actor:
                where_clauses.append("actor_id = ?")
                params.append(actor)
            if node_name:
                where_clauses.append("node_name = ?")
                params.append(node_name)
            if thread_id:
                where_clauses.append(
                    "(json_extract(details, '$.thread_id') = ? OR entity_id = ?)"
                )
                params.extend([thread_id, thread_id])
            if build_id:
                where_clauses.append("json_extract(details, '$.build_id') = ?")
                params.append(build_id)
            if date_from:
                where_clauses.append("timestamp >= ?")
                params.append(date_from)
            if date_to:
                where_clauses.append("timestamp <= ?")
                params.append(date_to + " 23:59:59")

            where = " AND ".join(where_clauses) if where_clauses else "1=1"

            count_row = conn.execute(
                f"SELECT COUNT(*) FROM audit_log WHERE {where}", params
            ).fetchone()
            total = count_row[0]

            offset = (page - 1) * page_size
            rows = conn.execute(
                f"SELECT * FROM audit_log WHERE {where} "
                f"ORDER BY timestamp DESC LIMIT ? OFFSET ?",
                params + [page_size, offset],
            ).fetchall()

            events = [self._row_to_dict(r) for r in rows]
        finally:
            conn.close()

        return events, total

    def get_summary(self) -> dict[str, Any]:
        """Aggregate counts for dashboard summary."""
        conn = self._get_db()
        try:
            total_24h = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE timestamp >= datetime('now', '-1 day')"
            ).fetchone()[0]

            total_7d = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE timestamp >= datetime('now', '-7 days')"
            ).fetchone()[0]

            type_rows = conn.execute(
                "SELECT entity_type, COUNT(*) as cnt FROM audit_log "
                "WHERE timestamp >= datetime('now', '-7 days') GROUP BY entity_type"
            ).fetchall()
            events_by_type = {r["entity_type"]: r["cnt"] for r in type_rows}

            action_rows = conn.execute(
                "SELECT action, COUNT(*) as cnt FROM audit_log "
                "WHERE timestamp >= datetime('now', '-7 days') GROUP BY action"
            ).fetchall()
            events_by_action = {r["action"]: r["cnt"] for r in action_rows}

            active_users = conn.execute(
                "SELECT COUNT(DISTINCT actor_id) FROM audit_log "
                "WHERE timestamp >= datetime('now', '-1 day') AND actor_id != 'system' AND actor_id IS NOT NULL"
            ).fetchone()[0]

            approvals = conn.execute(
                "SELECT COUNT(*) FROM audit_log "
                "WHERE action = 'approved' AND timestamp >= datetime('now', '-7 days')"
            ).fetchone()[0]

            rejections = conn.execute(
                "SELECT COUNT(*) FROM audit_log "
                "WHERE action = 'rejected' AND timestamp >= datetime('now', '-7 days')"
            ).fetchone()[0]
        finally:
            conn.close()

        return {
            "total_events_24h": total_24h,
            "total_events_7d": total_7d,
            "events_by_type": events_by_type,
            "events_by_action": events_by_action,
            "active_users_24h": active_users,
            "recent_approvals": approvals,
            "recent_rejections": rejections,
        }

    # -- Hashing -----------------------------------------------------------------

    @staticmethod
    def _hash(data: dict) -> str:
        """Compute SHA-256 hash of data for integrity verification."""
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()

    # -- Row conversion ----------------------------------------------------------

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        """Convert a sqlite3.Row to a dict matching the AuditEvent schema."""
        d = dict(row)
        # Map DB column actor_id -> actor for the API model
        d["actor"] = d.pop("actor_id", None)
        # Parse details JSON string back to dict
        if d.get("details") and isinstance(d["details"], str):
            try:
                d["details"] = json.loads(d["details"])
            except (json.JSONDecodeError, TypeError):
                d["details"] = {}
        elif not d.get("details"):
            d["details"] = {}
        return d


# ---------------------------------------------------------------------------
# Singleton for easy import across the codebase
# ---------------------------------------------------------------------------
audit_service = AuditService()
