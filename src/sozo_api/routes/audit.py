"""Audit log API routes.

The audit log is append-only and immutable. Every significant action in the
system creates an audit event. This is required for clinical governance and
regulatory compliance.

All endpoints now read from the real SQLite audit_log table.
"""
from __future__ import annotations

import csv
import io
import json
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from sozo_auth.rbac import Permission, require_permission

from .audit_service import audit_service

router = APIRouter(
    prefix="/api/audit",
    tags=["audit"],
    dependencies=[Depends(require_permission(Permission.VIEW_AUDIT))],
)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class AuditEvent(BaseModel):
    id: int
    entity_type: str  # protocol, patient, review, evidence, user, system
    entity_id: str
    action: str  # created, updated, status_changed, reviewed, approved, etc.
    actor: Optional[str] = None  # user email or "system"
    timestamp: datetime
    node_name: Optional[str] = None  # LangGraph node if applicable
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None
    details: dict = Field(default_factory=dict)


class AuditEventList(BaseModel):
    items: list[AuditEvent]
    total: int
    page: int
    page_size: int


class AuditSummary(BaseModel):
    """Dashboard summary of audit activity."""
    total_events_24h: int
    total_events_7d: int
    events_by_type: dict[str, int]
    events_by_action: dict[str, int]
    active_users_24h: int
    recent_approvals: int
    recent_rejections: int


class NodeTraceEntry(BaseModel):
    """LangGraph node execution trace for a specific protocol build."""
    node_name: str
    timestamp: datetime
    duration_ms: int
    input_hash: str
    output_hash: str
    decision: Optional[str] = None
    status: str  # success, error, skipped


class ProtocolBuildTrace(BaseModel):
    """Complete build trace for a protocol generation."""
    protocol_id: UUID
    build_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_duration_ms: int
    nodes: list[NodeTraceEntry]
    errors: list[dict]
    generation_method: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/events", response_model=AuditEventList)
async def list_audit_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    node_name: Optional[str] = None,
):
    """List audit events with filtering.

    Admin/operator only. Supports filtering by entity, action, actor, date range.
    Results are ordered by timestamp descending (newest first).
    """
    events, total = audit_service.query_events(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        node_name=node_name,
        date_from=str(date_from) if date_from else None,
        date_to=str(date_to) if date_to else None,
        page=page,
        page_size=page_size,
    )

    return AuditEventList(
        items=[AuditEvent(**e) for e in events],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/summary", response_model=AuditSummary)
async def get_audit_summary():
    """Get audit activity summary for dashboard."""
    summary = audit_service.get_summary()
    return AuditSummary(**summary)


@router.get("/entity/{entity_type}/{entity_id}")
async def get_entity_audit_trail(entity_type: str, entity_id: str):
    """Get complete audit trail for a specific entity.

    Useful for tracing all actions on a specific protocol or patient.
    """
    events, total = audit_service.query_events(
        entity_type=entity_type,
        entity_id=entity_id,
        page=1,
        page_size=1000,  # Return all events for entity
    )

    if not events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No audit events found for {entity_type}/{entity_id}",
        )

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "total_events": total,
        "events": [AuditEvent(**e) for e in events],
    }


@router.get("/build-trace/{build_id}", response_model=ProtocolBuildTrace)
async def get_build_trace(build_id: str):
    """Get LangGraph node execution trace for a protocol build.

    Shows each node's execution: timing, input/output hashes, decisions.
    Essential for debugging and regulatory review.
    """
    # Query audit_log for node_executed events with this build_id
    # We search all node-related events and filter by build_id in details
    events, _ = audit_service.query_events(
        action="node_executed",
        page=1,
        page_size=500,
    )

    build_events = [
        e for e in events
        if e.get("details", {}).get("build_id") == build_id
    ]

    if not build_events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No build trace found for build_id={build_id}",
        )

    # Sort by timestamp ascending for trace order
    build_events.sort(key=lambda e: e["timestamp"])

    nodes = []
    for e in build_events:
        details = e.get("details", {})
        nodes.append(NodeTraceEntry(
            node_name=e.get("node_name") or "unknown",
            timestamp=e["timestamp"],
            duration_ms=details.get("duration_ms", 0),
            input_hash=e.get("input_hash") or "",
            output_hash=e.get("output_hash") or "",
            decision=details.get("decision"),
            status=details.get("status", "success"),
        ))

    total_ms = sum(n.duration_ms for n in nodes)
    first_ts = datetime.fromisoformat(str(build_events[0]["timestamp"]))
    last_ts = datetime.fromisoformat(str(build_events[-1]["timestamp"]))

    # Try to extract protocol_id from the first event
    protocol_id_str = build_events[0].get("entity_id", "00000000-0000-4000-a000-000000000000")
    try:
        protocol_uuid = UUID(protocol_id_str)
    except ValueError:
        protocol_uuid = UUID("00000000-0000-4000-a000-000000000000")

    generation_method = build_events[0].get("details", {}).get("generation_method", "langgraph_v2")

    return ProtocolBuildTrace(
        protocol_id=protocol_uuid,
        build_id=build_id,
        started_at=first_ts,
        completed_at=last_ts + timedelta(milliseconds=nodes[-1].duration_ms) if nodes else last_ts,
        total_duration_ms=total_ms,
        nodes=nodes,
        errors=[],
        generation_method=generation_method,
    )


@router.get("/export")
async def export_audit_log(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    action: Optional[str] = None,
    actor: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    format: str = Query("json", pattern="^(json|csv)$"),
):
    """Export audit log for regulatory review.

    Returns downloadable JSON or CSV file.
    """
    events, _ = audit_service.query_events(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        date_from=str(date_from) if date_from else None,
        date_to=str(date_to) if date_to else None,
        page=1,
        page_size=10000,  # Export up to 10k events
    )

    serialized = [AuditEvent(**e).model_dump(mode="json") for e in events]

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"audit_export_{timestamp_str}"

    if format == "csv":
        output = io.StringIO()
        if serialized:
            fieldnames = list(serialized[0].keys())
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for event in serialized:
                row = {}
                for k, v in event.items():
                    row[k] = json.dumps(v) if isinstance(v, (dict, list)) else v
                writer.writerow(row)
        content = output.getvalue().encode("utf-8")
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}.csv"',
            },
        )

    # JSON export
    content = json.dumps(
        {"exported_at": datetime.now(timezone.utc).isoformat(), "total": len(serialized), "events": serialized},
        indent=2,
        default=str,
    ).encode("utf-8")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}.json"',
        },
    )


@router.get("/actions")
async def list_available_actions():
    """List all action types recorded in audit log."""
    return {
        "actions": [
            "created", "updated", "status_changed", "reviewed",
            "approved", "rejected", "evidence_refreshed",
            "personalized", "exported", "archived",
            "login", "logout", "permission_denied",
            "qa_override", "safety_check", "generation_started",
            "generation_completed", "generation_failed",
            "node_executed",
        ]
    }


@router.get("/entity-types")
async def list_entity_types():
    """List all entity types in audit log."""
    return {
        "entity_types": [
            "protocol", "protocol_version", "patient",
            "assessment", "review", "evidence",
            "user", "system", "treatment_session",
            "graph_run",
        ]
    }
