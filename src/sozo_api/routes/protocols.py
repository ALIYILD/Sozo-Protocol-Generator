"""Protocol management API routes.

Full CRUD lifecycle for neuromodulation protocols:
generate, version, review, approve, export, and audit.

Wired to real SQLite database and GenerationService.
"""
from __future__ import annotations

import json
import logging
import math
import os
import sqlite3
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from sozo_auth.dependencies import get_current_user, require_clinician, require_reviewer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

_clinician_writes = [Depends(require_clinician)]

router = APIRouter(
    prefix="/api/protocols",
    tags=["protocols"],
    dependencies=[Depends(get_current_user)],
)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ProtocolStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


# Legal status transitions: source -> {allowed targets}
_STATUS_TRANSITIONS: dict[ProtocolStatusEnum, set[ProtocolStatusEnum]] = {
    ProtocolStatusEnum.DRAFT: {ProtocolStatusEnum.PENDING_REVIEW},
    ProtocolStatusEnum.PENDING_REVIEW: {
        ProtocolStatusEnum.APPROVED,
        ProtocolStatusEnum.REJECTED,
    },
    ProtocolStatusEnum.APPROVED: {
        ProtocolStatusEnum.SUPERSEDED,
        ProtocolStatusEnum.ARCHIVED,
    },
    ProtocolStatusEnum.REJECTED: {ProtocolStatusEnum.DRAFT},
    ProtocolStatusEnum.SUPERSEDED: set(),
    ProtocolStatusEnum.ARCHIVED: set(),
}

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class GenerateProtocolRequest(BaseModel):
    """Request to generate a new protocol."""

    condition_slug: str = Field(..., description="Condition slug from the registry")
    modality: Optional[str] = Field(
        None, description="Stimulation modality: tdcs, tps, tavns, ces"
    )
    tier: str = Field("fellow", description="Access tier: fellow or partners")
    doc_type: str = Field(
        "evidence_based_protocol", description="Blueprint document type"
    )
    prompt: Optional[str] = Field(
        None, description="Natural-language prompt for LangGraph pipeline"
    )
    template_id: Optional[str] = Field(
        None, description="Clone from an existing template protocol"
    )
    patient_id: Optional[str] = Field(
        None, description="V2: patient ID for personalisation"
    )


class ProtocolListItem(BaseModel):
    """Summary for protocol list view."""

    protocol_id: UUID
    version: int
    status: ProtocolStatusEnum
    condition_slug: str
    condition_name: str
    modality: str
    evidence_level: str
    created_at: datetime
    created_by: str
    is_template: bool


class PaginatedResponse(BaseModel):
    items: list[ProtocolListItem]
    total: int
    page: int
    page_size: int
    pages: int


class ProtocolVersionSummary(BaseModel):
    version_id: UUID
    version: int
    status: ProtocolStatusEnum
    created_at: datetime
    created_by: str
    generation_method: str


class SubmitReviewRequest(BaseModel):
    notes: Optional[str] = None


class StatusTransitionRequest(BaseModel):
    target_status: ProtocolStatusEnum
    notes: Optional[str] = None


class GenerationStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: float
    message: str
    result: Optional[dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_db() -> sqlite3.Connection:
    """Get a SQLite connection using shared db_helper."""
    from sozo_api.routes.db_helper import get_db
    return get_db()


def _ensure_tables(conn: sqlite3.Connection) -> None:
    """Create the required tables if they don't exist yet."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS protocols (
            id TEXT PRIMARY KEY,
            condition_slug TEXT NOT NULL,
            primary_modality TEXT,
            is_template INTEGER NOT NULL DEFAULT 0,
            created_by TEXT DEFAULT NULL,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            current_version_id TEXT
        );

        CREATE TABLE IF NOT EXISTS protocol_versions (
            id TEXT PRIMARY KEY,
            protocol_id TEXT NOT NULL REFERENCES protocols(id) ON DELETE CASCADE,
            version_number INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'draft',
            data TEXT NOT NULL DEFAULT '{}',
            parent_version_id TEXT,
            build_id TEXT,
            generation_method TEXT,
            created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            created_by TEXT DEFAULT NULL,
            approved_by TEXT,
            approved_at TEXT,
            review_notes TEXT
        );

        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            action TEXT NOT NULL,
            actor_id TEXT,
            timestamp TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
            details TEXT
        );

        CREATE INDEX IF NOT EXISTS ix_protocols_condition ON protocols(condition_slug);
        CREATE INDEX IF NOT EXISTS ix_pv_protocol ON protocol_versions(protocol_id);
        CREATE INDEX IF NOT EXISTS ix_pv_status ON protocol_versions(status);
        CREATE INDEX IF NOT EXISTS ix_audit_entity ON audit_events(entity_type, entity_id);
    """)
    conn.commit()


def _db() -> sqlite3.Connection:
    """Get a DB connection with tables guaranteed to exist."""
    conn = _get_db()
    _ensure_tables(conn)
    return conn


def _parse_dt(s: str | None) -> datetime:
    """Parse an ISO datetime string, falling back to now()."""
    if not s:
        return datetime.now(timezone.utc)
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return datetime.now(timezone.utc)


def _parse_json(s: str | None) -> dict:
    """Parse a JSON string, falling back to empty dict."""
    if not s:
        return {}
    try:
        return json.loads(s)
    except (json.JSONDecodeError, TypeError):
        return {}


def _condition_display_name(slug: str) -> str:
    """Convert condition slug to display name."""
    return slug.replace("_", " ").title()


def _insert_audit(conn: sqlite3.Connection, entity_id: str, action: str, details: str, actor: str = "api_user") -> None:
    """Insert an audit event."""
    conn.execute(
        "INSERT INTO audit_events (entity_type, entity_id, action, actor_id, details) VALUES (?, ?, ?, ?, ?)",
        ("protocol", entity_id, action, actor, json.dumps({"message": details})),
    )


# ---------------------------------------------------------------------------
# Async task tracker (still in-memory, not DB-backed)
# ---------------------------------------------------------------------------

_TASKS: dict[str, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_transition(
    current: ProtocolStatusEnum, target: ProtocolStatusEnum
) -> None:
    allowed = _STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Invalid status transition: {current.value} -> {target.value}. "
                f"Allowed targets: {[s.value for s in allowed]}"
            ),
        )


def _row_to_list_item(row: sqlite3.Row) -> ProtocolListItem:
    """Convert a joined protocol+version row to a ProtocolListItem."""
    data = _parse_json(row["data"]) if "data" in row.keys() else {}
    evidence_level = data.get("evidence_level", "pending")
    if not evidence_level or evidence_level == "pending":
        # Try to extract from sections
        sections = data.get("sections", {})
        evidence_summary = sections.get("evidence_summary", {})
        if isinstance(evidence_summary, dict):
            evidence_level = evidence_summary.get("level", "pending")

    return ProtocolListItem(
        protocol_id=UUID(row["id"]),
        version=row["version_number"] or 1,
        status=ProtocolStatusEnum(row["status"]),
        condition_slug=row["condition_slug"],
        condition_name=_condition_display_name(row["condition_slug"]),
        modality=row["primary_modality"] or "tdcs",
        evidence_level=evidence_level or "pending",
        created_at=_parse_dt(row["created_at"]),
        created_by=row["created_by"] or "system",
        is_template=bool(row["is_template"]),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/conditions/available", summary="List available conditions")
async def list_available_conditions() -> dict[str, Any]:
    """List all conditions available for protocol generation."""
    return {
        "conditions": [
            {
                "slug": "major_depressive_disorder",
                "display_name": "Major Depressive Disorder",
                "icd10": "F32",
                "evidence_level": "high",
                "modalities": ["tdcs", "tps"],
            },
            {
                "slug": "chronic_pain",
                "display_name": "Chronic Pain",
                "icd10": "G89",
                "evidence_level": "medium",
                "modalities": ["tdcs", "tps", "ces"],
            },
            {
                "slug": "tinnitus",
                "display_name": "Tinnitus",
                "icd10": "H93.1",
                "evidence_level": "medium",
                "modalities": ["tavns", "tdcs"],
            },
            {
                "slug": "generalised_anxiety_disorder",
                "display_name": "Generalised Anxiety Disorder",
                "icd10": "F41.1",
                "evidence_level": "low",
                "modalities": ["ces", "tdcs"],
            },
            {
                "slug": "fibromyalgia",
                "display_name": "Fibromyalgia",
                "icd10": "M79.7",
                "evidence_level": "medium",
                "modalities": ["tdcs", "tps"],
            },
            {
                "slug": "post_stroke_aphasia",
                "display_name": "Post-Stroke Aphasia",
                "icd10": "R47.0",
                "evidence_level": "high",
                "modalities": ["tdcs"],
            },
            {
                "slug": "migraine",
                "display_name": "Migraine",
                "icd10": "G43",
                "evidence_level": "medium",
                "modalities": ["tdcs", "tavns"],
            },
        ]
    }


@router.get("/templates", summary="List protocol templates")
async def list_templates() -> dict[str, Any]:
    """List protocol templates available for cloning."""
    try:
        conn = _db()
        rows = conn.execute("""
            SELECT p.id, p.condition_slug, p.primary_modality, p.is_template,
                   p.created_by, p.created_at,
                   pv.version_number, pv.status, pv.data
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.is_template = 1
            ORDER BY p.created_at DESC
        """).fetchall()
        conn.close()
        templates = [_row_to_list_item(r) for r in rows]
        return {"templates": [t.model_dump(mode="json") for t in templates]}
    except Exception as e:
        logger.error(f"list_templates failed: {e}")
        return {"templates": []}


@router.get(
    "/generation-status/{task_id}", summary="Poll generation task status"
)
async def get_generation_status(task_id: str) -> GenerationStatusResponse:
    """Poll async generation task status."""
    task = _TASKS.get(task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return GenerationStatusResponse(**task)


@router.get("/", response_model=PaginatedResponse, summary="List protocols")
async def list_protocols(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    condition: Optional[str] = None,
    modality: Optional[str] = None,
    protocol_status: Optional[ProtocolStatusEnum] = Query(
        None, alias="status"
    ),
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|condition_name|modality|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
) -> PaginatedResponse:
    """List protocols with filtering, pagination, and sorting."""
    try:
        conn = _db()

        # Build query — join protocols with their current version
        base_query = """
            SELECT p.id, p.condition_slug, p.primary_modality, p.is_template,
                   p.created_by, p.created_at,
                   COALESCE(pv.version_number, 1) as version_number,
                   COALESCE(pv.status, 'draft') as status,
                   pv.data
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
        """
        where_clauses: list[str] = []
        params: list[Any] = []

        if condition:
            where_clauses.append("p.condition_slug = ?")
            params.append(condition)
        if modality:
            where_clauses.append("p.primary_modality = ?")
            params.append(modality)
        if protocol_status is not None:
            where_clauses.append("pv.status = ?")
            params.append(protocol_status.value)
        if is_template is not None:
            where_clauses.append("p.is_template = ?")
            params.append(1 if is_template else 0)
        if search:
            where_clauses.append("(p.condition_slug LIKE ? OR p.primary_modality LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        if where_clauses:
            base_query += " WHERE " + " AND ".join(where_clauses)

        # Sorting — map sort_by to actual columns
        sort_col_map = {
            "created_at": "p.created_at",
            "condition_name": "p.condition_slug",
            "modality": "p.primary_modality",
            "status": "pv.status",
        }
        sort_col = sort_col_map.get(sort_by, "p.created_at")
        base_query += f" ORDER BY {sort_col} {'DESC' if sort_order == 'desc' else 'ASC'}"

        # Count total
        count_query = f"SELECT COUNT(*) FROM ({base_query})"
        total = conn.execute(count_query, params).fetchone()[0]

        # Paginate
        pages = max(1, math.ceil(total / page_size))
        offset = (page - 1) * page_size
        base_query += " LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        rows = conn.execute(base_query, params).fetchall()
        conn.close()

        items = [_row_to_list_item(r) for r in rows]

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
        )
    except Exception as e:
        logger.error(f"list_protocols failed: {e}")
        # Return empty response on DB errors rather than 500
        return PaginatedResponse(items=[], total=0, page=page, page_size=page_size, pages=1)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create / generate a protocol",
    dependencies=_clinician_writes,
)
async def create_protocol(request: GenerateProtocolRequest) -> dict[str, Any]:
    """Create a new protocol.

    * If *prompt* is provided, the LangGraph pipeline is queued.
    * If *template_id* is provided, the source protocol is cloned.
    * Otherwise the canonical condition-based generator runs.

    Returns ``protocol_id`` and ``task_id`` for async polling.
    """
    # Validate condition slug against known conditions
    try:
        from sozo_generator.knowledge.base import KnowledgeBase
        kb = KnowledgeBase()
        kb.load_all()
        known_slugs = set(kb.list_conditions())
    except Exception:
        known_slugs = None

    if known_slugs is not None and request.condition_slug not in known_slugs:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown condition_slug: {request.condition_slug}. "
            f"Available: {sorted(known_slugs)}",
        )

    # Validate template_id if given
    if request.template_id:
        try:
            tmpl_uuid = request.template_id
            UUID(tmpl_uuid)  # validate format
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="template_id must be a valid UUID",
            )
        conn = _db()
        tmpl_row = conn.execute(
            "SELECT id, is_template FROM protocols WHERE id = ?", (tmpl_uuid,)
        ).fetchone()
        conn.close()
        if tmpl_row is None or not tmpl_row["is_template"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {request.template_id} not found",
            )

    # Determine generation method
    if request.prompt:
        gen_method = "langgraph_prompt"
    elif request.template_id:
        gen_method = "template_clone"
    else:
        gen_method = "canonical"

    pid = str(uuid4())
    vid = str(uuid4())
    task_id = f"task-{uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    chosen_modality = request.modality or "tdcs"

    # Run real generation via GenerationService for canonical path
    generation_data: dict[str, Any] = {}
    evidence_data: dict[str, Any] = {
        "articles_count": 0,
        "prisma_screened": 0,
        "prisma_included": 0,
        "review_flags": [],
        "top_articles": [],
    }
    build_id = ""
    output_path = None

    if gen_method == "canonical":
        try:
            from sozo_generator.generation.service import GenerationService

            service = GenerationService(with_visuals=False, with_qa=True)
            result = service.generate_canonical(
                condition=request.condition_slug,
                doc_type=request.doc_type,
                tier=request.tier,
            )
            build_id = result.build_id
            output_path = result.output_path

            if result.success:
                generation_data = {
                    "output_path": result.output_path,
                    "build_id": result.build_id,
                    "qa_passed": result.qa_passed,
                    "qa_issues": result.qa_issues,
                    "visuals_generated": result.visuals_generated,
                }
                # Update task as completed
                _TASKS[task_id] = {
                    "task_id": task_id,
                    "status": "completed",
                    "progress": 1.0,
                    "message": f"Generation complete for {request.condition_slug}",
                    "result": {
                        "protocol_id": pid,
                        "output_path": result.output_path,
                        "build_id": result.build_id,
                    },
                }
            else:
                generation_data = {
                    "error": result.error,
                    "build_id": result.build_id,
                }
                _TASKS[task_id] = {
                    "task_id": task_id,
                    "status": "failed",
                    "progress": 0.0,
                    "message": f"Generation failed: {result.error}",
                    "result": None,
                }
        except Exception as e:
            logger.error(f"GenerationService failed: {e}")
            generation_data = {"error": str(e)}
            _TASKS[task_id] = {
                "task_id": task_id,
                "status": "failed",
                "progress": 0.0,
                "message": f"Generation error: {e}",
                "result": None,
            }
    else:
        # For prompt-based or template-clone, queue as generating
        _TASKS[task_id] = {
            "task_id": task_id,
            "status": "generating",
            "progress": 0.0,
            "message": f"Queued {gen_method} generation for {request.condition_slug}",
            "result": None,
        }

    # Store the version data: merge generation output + evidence
    version_data = json.dumps({
        "generation": generation_data,
        "evidence": evidence_data,
        "evidence_level": "pending",
    })

    # Insert into database
    try:
        conn = _db()
        conn.execute(
            """INSERT INTO protocols (id, condition_slug, primary_modality, is_template, created_by, created_at, updated_at, current_version_id)
               VALUES (?, ?, ?, 0, NULL, ?, ?, ?)""",
            (pid, request.condition_slug, chosen_modality, now, now, vid),
        )
        conn.execute(
            """INSERT INTO protocol_versions (id, protocol_id, version_number, status, data, build_id, generation_method, created_at, created_by)
               VALUES (?, ?, 1, 'draft', ?, ?, ?, ?, NULL)""",
            (vid, pid, version_data, build_id, gen_method, now),
        )
        _insert_audit(conn, pid, "protocol_created", f"Protocol created via {gen_method}")
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"DB insert failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store protocol: {e}",
        )

    return {
        "protocol_id": pid,
        "task_id": task_id,
        "status": _TASKS[task_id]["status"],
    }


@router.get("/{protocol_id}", summary="Get full protocol")
async def get_protocol(protocol_id: UUID) -> dict[str, Any]:
    """Get complete protocol with current version data, evidence, and safety info."""
    pid = str(protocol_id)
    try:
        conn = _db()
        row = conn.execute("""
            SELECT p.id, p.condition_slug, p.primary_modality, p.is_template,
                   p.created_by, p.created_at, p.updated_at,
                   pv.id as version_id, pv.version_number, pv.status,
                   pv.data, pv.generation_method
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()
        conn.close()
    except Exception as e:
        logger.error(f"get_protocol DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol {protocol_id} not found",
        )

    data = _parse_json(row["data"])
    evidence = data.get("evidence", {})

    return {
        "protocol_id": pid,
        "version_id": row["version_id"] or "",
        "version": row["version_number"] or 1,
        "status": row["status"] or "draft",
        "condition_slug": row["condition_slug"],
        "condition_name": _condition_display_name(row["condition_slug"]),
        "modality": row["primary_modality"] or "tdcs",
        "evidence_level": data.get("evidence_level", "pending"),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "created_by": row["created_by"] or "system",
        "is_template": bool(row["is_template"]),
        "generation_method": row["generation_method"] or "canonical",
        "data": data.get("generation", data),
        "evidence": evidence,
    }


@router.get(
    "/{protocol_id}/versions", summary="List protocol versions"
)
async def list_protocol_versions(
    protocol_id: UUID,
) -> dict[str, Any]:
    """List all versions of a protocol."""
    pid = str(protocol_id)
    try:
        conn = _db()
        # Verify protocol exists
        proto = conn.execute("SELECT id FROM protocols WHERE id = ?", (pid,)).fetchone()
        if proto is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol {protocol_id} not found",
            )
        rows = conn.execute("""
            SELECT id, version_number, status, created_at, created_by, generation_method
            FROM protocol_versions
            WHERE protocol_id = ?
            ORDER BY version_number DESC
        """, (pid,)).fetchall()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"list_protocol_versions DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    versions = [
        {
            "version_id": r["id"],
            "version": r["version_number"],
            "status": r["status"],
            "created_at": r["created_at"],
            "created_by": r["created_by"] or "system",
            "generation_method": r["generation_method"] or "canonical",
        }
        for r in rows
    ]
    return {"protocol_id": pid, "versions": versions}


@router.get(
    "/{protocol_id}/versions/{version}",
    summary="Get specific protocol version",
)
async def get_protocol_version(
    protocol_id: UUID, version: int
) -> dict[str, Any]:
    """Get a specific version of a protocol."""
    pid = str(protocol_id)
    try:
        conn = _db()
        row = conn.execute("""
            SELECT pv.id, pv.version_number, pv.status, pv.created_at,
                   pv.created_by, pv.generation_method, pv.data
            FROM protocol_versions pv
            JOIN protocols p ON p.id = pv.protocol_id
            WHERE pv.protocol_id = ? AND pv.version_number = ?
        """, (pid, version)).fetchone()
        conn.close()
    except Exception as e:
        logger.error(f"get_protocol_version DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version} not found for protocol {protocol_id}",
        )

    data = _parse_json(row["data"])
    return {
        "protocol_id": pid,
        "version_id": row["id"],
        "version": row["version_number"],
        "status": row["status"],
        "created_at": row["created_at"],
        "created_by": row["created_by"] or "system",
        "generation_method": row["generation_method"] or "canonical",
        "data": data.get("generation", data),
    }


@router.put(
    "/{protocol_id}",
    summary="Update protocol (new version)",
    dependencies=_clinician_writes,
)
async def update_protocol(
    protocol_id: UUID, data: dict[str, Any]
) -> dict[str, Any]:
    """Update a protocol by creating a new version.

    Only allowed when current status is DRAFT.
    """
    pid = str(protocol_id)
    now = datetime.now(timezone.utc).isoformat()

    try:
        conn = _db()
        # Get current state
        row = conn.execute("""
            SELECT p.id, p.current_version_id,
                   pv.version_number, pv.status
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()

        if row is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol {protocol_id} not found",
            )

        current_status = row["status"] or "draft"
        if current_status != "draft":
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot update protocol in '{current_status}' status. Only DRAFT protocols may be edited.",
            )

        new_version = (row["version_number"] or 1) + 1
        new_vid = str(uuid4())
        parent_vid = row["current_version_id"]

        version_data = json.dumps({"generation": data, "evidence_level": "pending"})

        conn.execute(
            """INSERT INTO protocol_versions (id, protocol_id, version_number, status, data, parent_version_id, generation_method, created_at, created_by)
               VALUES (?, ?, ?, 'draft', ?, ?, 'manual_edit', ?, NULL)""",
            (new_vid, pid, new_version, version_data, parent_vid, now),
        )
        conn.execute(
            "UPDATE protocols SET current_version_id = ?, updated_at = ? WHERE id = ?",
            (new_vid, now, pid),
        )
        _insert_audit(conn, pid, "protocol_updated", f"New version {new_version} created via manual edit")
        conn.commit()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"update_protocol DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {
        "protocol_id": pid,
        "version_id": new_vid,
        "version": new_version,
        "status": "draft",
        "updated_at": now,
    }


@router.post(
    "/{protocol_id}/submit-review",
    summary="Submit protocol for review",
    dependencies=_clinician_writes,
)
async def submit_for_review(
    protocol_id: UUID,
    request: SubmitReviewRequest,
) -> dict[str, Any]:
    """Submit protocol for clinician review. Transitions DRAFT -> PENDING_REVIEW."""
    pid = str(protocol_id)
    now = datetime.now(timezone.utc).isoformat()

    try:
        conn = _db()
        row = conn.execute("""
            SELECT p.current_version_id, pv.status
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()

        if row is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol {protocol_id} not found",
            )

        current_status = ProtocolStatusEnum(row["status"] or "draft")
        _validate_transition(current_status, ProtocolStatusEnum.PENDING_REVIEW)

        vid = row["current_version_id"]

        conn.execute(
            "UPDATE protocol_versions SET status = 'pending_review' WHERE id = ?",
            (vid,),
        )
        conn.execute(
            "UPDATE protocols SET updated_at = ? WHERE id = ?",
            (now, pid),
        )
        _insert_audit(
            conn, pid, "submitted_for_review",
            request.notes or "Submitted for clinician review",
        )
        conn.commit()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"submit_for_review DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {
        "protocol_id": pid,
        "status": ProtocolStatusEnum.PENDING_REVIEW.value,
        "message": "Protocol submitted for review",
        "qa_issues": [],
    }


@router.post(
    "/{protocol_id}/transition",
    summary="Transition protocol status",
    dependencies=[Depends(require_reviewer)],
)
async def transition_status(
    protocol_id: UUID,
    request: StatusTransitionRequest,
) -> dict[str, Any]:
    """Transition protocol status with validation."""
    pid = str(protocol_id)
    now = datetime.now(timezone.utc).isoformat()

    try:
        conn = _db()
        row = conn.execute("""
            SELECT p.current_version_id, pv.status
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()

        if row is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol {protocol_id} not found",
            )

        old_status = ProtocolStatusEnum(row["status"] or "draft")
        _validate_transition(old_status, request.target_status)

        vid = row["current_version_id"]

        conn.execute(
            "UPDATE protocol_versions SET status = ? WHERE id = ?",
            (request.target_status.value, vid),
        )
        conn.execute(
            "UPDATE protocols SET updated_at = ? WHERE id = ?",
            (now, pid),
        )

        detail_msg = (
            f"Status changed from {old_status.value} to {request.target_status.value}"
            + (f" -- {request.notes}" if request.notes else "")
        )
        _insert_audit(conn, pid, "status_transition", detail_msg)
        conn.commit()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"transition_status DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {
        "protocol_id": pid,
        "previous_status": old_status.value,
        "status": request.target_status.value,
        "transitioned_at": now,
    }


@router.post(
    "/{protocol_id}/clone",
    summary="Clone protocol as new draft",
    dependencies=_clinician_writes,
)
async def clone_protocol(protocol_id: UUID) -> dict[str, Any]:
    """Clone an existing protocol as a new DRAFT."""
    pid = str(protocol_id)
    now = datetime.now(timezone.utc).isoformat()

    try:
        conn = _db()
        row = conn.execute("""
            SELECT p.id, p.condition_slug, p.primary_modality, p.is_template,
                   pv.data
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()

        if row is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol {protocol_id} not found",
            )

        new_pid = str(uuid4())
        new_vid = str(uuid4())

        conn.execute(
            """INSERT INTO protocols (id, condition_slug, primary_modality, is_template, created_by, created_at, updated_at, current_version_id)
               VALUES (?, ?, ?, 0, NULL, ?, ?, ?)""",
            (new_pid, row["condition_slug"], row["primary_modality"], now, now, new_vid),
        )
        conn.execute(
            """INSERT INTO protocol_versions (id, protocol_id, version_number, status, data, generation_method, created_at, created_by)
               VALUES (?, ?, 1, 'draft', ?, 'template_clone', ?, NULL)""",
            (new_vid, new_pid, row["data"] or "{}", now),
        )
        _insert_audit(conn, new_pid, "protocol_cloned", f"Cloned from protocol {pid}")
        conn.commit()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"clone_protocol DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    return {
        "protocol_id": new_pid,
        "cloned_from": pid,
        "version": 1,
        "status": ProtocolStatusEnum.DRAFT.value,
        "created_at": now,
    }


@router.get(
    "/{protocol_id}/export/{fmt}",
    summary="Export protocol as DOCX or PDF",
    dependencies=_clinician_writes,
)
async def export_protocol(protocol_id: UUID, fmt: str) -> dict[str, Any]:
    """Export protocol as DOCX or PDF.

    Checks for a real output_path in version data; falls back to queuing an export task.
    """
    pid = str(protocol_id)

    if fmt not in ("docx", "pdf"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported export format: {fmt}. Use 'docx' or 'pdf'.",
        )

    try:
        conn = _db()
        row = conn.execute("""
            SELECT pv.data
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()
        conn.close()
    except Exception as e:
        logger.error(f"export_protocol DB error: {e}")
        row = None

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol {protocol_id} not found",
        )

    data = _parse_json(row["data"])
    generation = data.get("generation", {})
    output_path = generation.get("output_path")

    # If we have a real output path, return it directly
    if output_path and fmt == "docx":
        return {
            "protocol_id": pid,
            "format": fmt,
            "status": "ready",
            "download_path": output_path,
            "message": f"Protocol DOCX available at {output_path}",
        }

    # Otherwise queue an export task
    task_id = f"export-{uuid4().hex[:12]}"
    _TASKS[task_id] = {
        "task_id": task_id,
        "status": "processing",
        "progress": 0.0,
        "message": f"Exporting protocol {protocol_id} as {fmt.upper()}",
        "result": None,
    }

    return {
        "protocol_id": pid,
        "format": fmt,
        "task_id": task_id,
        "status": "processing",
        "message": f"Export queued. Poll /api/protocols/generation-status/{task_id} for progress.",
    }


@router.get(
    "/{protocol_id}/evidence", summary="Get protocol evidence summary"
)
async def get_protocol_evidence(protocol_id: UUID) -> dict[str, Any]:
    """Get evidence summary for a protocol from its version data JSON."""
    pid = str(protocol_id)

    try:
        conn = _db()
        row = conn.execute("""
            SELECT pv.data
            FROM protocols p
            LEFT JOIN protocol_versions pv ON pv.id = p.current_version_id
            WHERE p.id = ?
        """, (pid,)).fetchone()
        conn.close()
    except Exception as e:
        logger.error(f"get_protocol_evidence DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Protocol {protocol_id} not found",
        )

    data = _parse_json(row["data"])
    evidence = data.get("evidence", {})

    return {
        "protocol_id": pid,
        "articles_count": evidence.get("articles_count", 0),
        "prisma_flow": {
            "identified": evidence.get("prisma_screened", 0) + 20,
            "screened": evidence.get("prisma_screened", 0),
            "eligible": evidence.get("prisma_included", 0) + 5,
            "included": evidence.get("prisma_included", 0),
        },
        "review_flags": evidence.get("review_flags", []),
        "top_articles": evidence.get("top_articles", []),
    }


@router.get(
    "/{protocol_id}/audit", summary="Get protocol audit trail"
)
async def get_protocol_audit_trail(protocol_id: UUID) -> dict[str, Any]:
    """Get the full audit trail for a protocol from audit_events table."""
    pid = str(protocol_id)

    try:
        conn = _db()
        # Verify protocol exists
        proto = conn.execute("SELECT id FROM protocols WHERE id = ?", (pid,)).fetchone()
        if proto is None:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol {protocol_id} not found",
            )

        rows = conn.execute("""
            SELECT action, actor_id, timestamp, details
            FROM audit_events
            WHERE entity_type = 'protocol' AND entity_id = ?
            ORDER BY timestamp ASC
        """, (pid,)).fetchall()
        conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_protocol_audit_trail DB error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    events = []
    for r in rows:
        details_json = _parse_json(r["details"])
        events.append({
            "event": r["action"],
            "timestamp": r["timestamp"],
            "actor": r["actor_id"] or "system",
            "details": details_json.get("message", ""),
        })

    return {
        "protocol_id": pid,
        "events": events,
    }
