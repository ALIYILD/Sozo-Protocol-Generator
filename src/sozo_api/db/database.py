"""
SQLite Database — schema creation, connection management, and CRUD helpers.

Tables: users, protocols, evidence, protocol_evidence, reviews, uploads, audit_log
"""
from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/sozo.db")


def _uid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:12]}"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_password(password: str) -> str:
    """Simple SHA-256 hash. Replace with bcrypt in production."""
    return hashlib.sha256(password.encode()).hexdigest()


# ── Schema ────────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'clinician',
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS protocols (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    condition_slug TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'fellow',
    doc_type TEXT NOT NULL DEFAULT 'evidence_based_protocol',
    source TEXT NOT NULL DEFAULT 'generated',
    status TEXT NOT NULL DEFAULT 'draft',
    version INTEGER NOT NULL DEFAULT 1,
    schema_json TEXT NOT NULL DEFAULT '{}',
    provenance_json TEXT DEFAULT '{}',
    created_by TEXT REFERENCES users(id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evidence (
    id TEXT PRIMARY KEY,
    pmid TEXT,
    doi TEXT,
    title TEXT NOT NULL,
    authors TEXT,
    journal TEXT,
    year INTEGER,
    evidence_type TEXT,
    evidence_level TEXT,
    abstract TEXT,
    cached_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS protocol_evidence (
    protocol_id TEXT REFERENCES protocols(id),
    evidence_id TEXT REFERENCES evidence(id),
    section_slug TEXT NOT NULL,
    confidence TEXT,
    attached_by TEXT REFERENCES users(id),
    attached_at TEXT NOT NULL,
    PRIMARY KEY (protocol_id, evidence_id, section_slug)
);

CREATE TABLE IF NOT EXISTS reviews (
    id TEXT PRIMARY KEY,
    protocol_id TEXT REFERENCES protocols(id) NOT NULL,
    reviewer_id TEXT REFERENCES users(id) NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT,
    section_comments TEXT DEFAULT '{}',
    decided_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS uploads (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    extraction_status TEXT DEFAULT 'pending',
    extracted_schema TEXT DEFAULT '{}',
    corrections_json TEXT DEFAULT '{}',
    protocol_id TEXT REFERENCES protocols(id),
    uploaded_by TEXT REFERENCES users(id),
    uploaded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_log (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    detail TEXT,
    timestamp TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_protocols_condition ON protocols(condition_slug);
CREATE INDEX IF NOT EXISTS idx_protocols_status ON protocols(status);
CREATE INDEX IF NOT EXISTS idx_evidence_pmid ON evidence(pmid);
CREATE INDEX IF NOT EXISTS idx_reviews_protocol ON reviews(protocol_id);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log(resource_type, resource_id);
"""


# ── Database Class ────────────────────────────────────────────────────────


class SozoDB:
    """SQLite database for SOZO platform."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def init_schema(self):
        """Create all tables if they don't exist."""
        self.conn.executescript(SCHEMA_SQL)
        self.conn.commit()
        logger.info(f"Database initialized: {self.db_path}")

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    # ── Users ─────────────────────────────────────────────────────────

    def create_user(self, email: str, name: str, password: str, role: str = "clinician") -> dict:
        user_id = _uid("user-")
        self.conn.execute(
            "INSERT INTO users (id, email, name, role, password_hash, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, email, name, role, _hash_password(password), _now()),
        )
        self.conn.commit()
        self._audit("create_user", "user", user_id)
        return {"id": user_id, "email": email, "name": name, "role": role}

    def authenticate(self, email: str, password: str) -> Optional[dict]:
        row = self.conn.execute(
            "SELECT * FROM users WHERE email=? AND password_hash=?",
            (email, _hash_password(password)),
        ).fetchone()
        if row:
            return dict(row)
        return None

    def get_user(self, user_id: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row) if row else None

    def list_users(self) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT id, email, name, role, created_at FROM users").fetchall()]

    # ── Protocols ─────────────────────────────────────────────────────

    def create_protocol(self, name: str, condition_slug: str, tier: str, doc_type: str,
                        source: str, schema_json: dict, created_by: str = "", provenance_json: dict = None) -> dict:
        proto_id = _uid("proto-")
        now = _now()
        self.conn.execute(
            "INSERT INTO protocols (id,name,condition_slug,tier,doc_type,source,status,version,schema_json,provenance_json,created_by,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (proto_id, name, condition_slug, tier, doc_type, source, "draft", 1,
             json.dumps(schema_json), json.dumps(provenance_json or {}), created_by or None, now, now),
        )
        self.conn.commit()
        self._audit("create_protocol", "protocol", proto_id, user_id=created_by)
        return {"id": proto_id, "name": name, "condition_slug": condition_slug, "status": "draft"}

    def get_protocol(self, proto_id: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM protocols WHERE id=?", (proto_id,)).fetchone()
        if row:
            d = dict(row)
            d["schema_json"] = json.loads(d["schema_json"])
            d["provenance_json"] = json.loads(d["provenance_json"]) if d.get("provenance_json") else {}
            return d
        return None

    def list_protocols(self, condition: str = "", tier: str = "", status: str = "", limit: int = 100) -> list[dict]:
        query = "SELECT id, name, condition_slug, tier, doc_type, source, status, version, created_at, updated_at FROM protocols WHERE 1=1"
        params = []
        if condition:
            query += " AND condition_slug=?"
            params.append(condition)
        if tier:
            query += " AND tier=?"
            params.append(tier)
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self.conn.execute(query, params).fetchall()]

    def update_protocol_status(self, proto_id: str, status: str, user_id: str = "") -> bool:
        self.conn.execute(
            "UPDATE protocols SET status=?, updated_at=? WHERE id=?",
            (status, _now(), proto_id),
        )
        self.conn.commit()
        self._audit("update_status", "protocol", proto_id, detail=status, user_id=user_id)
        return True

    # ── Evidence ──────────────────────────────────────────────────────

    def upsert_evidence(self, pmid: str, title: str, authors: str = "", journal: str = "",
                        year: int = 0, evidence_type: str = "", evidence_level: str = "medium",
                        abstract: str = "", doi: str = "") -> str:
        ev_id = f"ev-{pmid}" if pmid else _uid("ev-")
        existing = self.conn.execute("SELECT id FROM evidence WHERE pmid=?", (pmid,)).fetchone()
        if existing:
            return existing["id"]
        self.conn.execute(
            "INSERT INTO evidence (id,pmid,doi,title,authors,journal,year,evidence_type,evidence_level,abstract,cached_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (ev_id, pmid, doi, title, authors, journal, year, evidence_type, evidence_level, abstract, _now()),
        )
        self.conn.commit()
        return ev_id

    def get_evidence(self, pmid: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM evidence WHERE pmid=?", (pmid,)).fetchone()
        return dict(row) if row else None

    def attach_evidence(self, protocol_id: str, evidence_id: str, section_slug: str,
                        confidence: str = "medium", attached_by: str = ""):
        self.conn.execute(
            "INSERT OR REPLACE INTO protocol_evidence (protocol_id,evidence_id,section_slug,confidence,attached_by,attached_at) VALUES (?,?,?,?,?,?)",
            (protocol_id, evidence_id, section_slug, confidence, attached_by or None, _now()),
        )
        self.conn.commit()

    def get_protocol_evidence(self, protocol_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT pe.*, e.pmid, e.title, e.evidence_level FROM protocol_evidence pe JOIN evidence e ON pe.evidence_id=e.id WHERE pe.protocol_id=?",
            (protocol_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Reviews ───────────────────────────────────────────────────────

    def create_review(self, protocol_id: str, reviewer_id: str, decision: str,
                      reason: str = "", section_comments: dict = None) -> str:
        rev_id = _uid("rev-")
        self.conn.execute(
            "INSERT INTO reviews (id,protocol_id,reviewer_id,decision,reason,section_comments,decided_at) VALUES (?,?,?,?,?,?,?)",
            (rev_id, protocol_id, reviewer_id, decision, reason, json.dumps(section_comments or {}), _now()),
        )
        # Update protocol status
        if decision == "approve":
            self.update_protocol_status(protocol_id, "approved", reviewer_id)
        elif decision == "reject":
            self.update_protocol_status(protocol_id, "draft", reviewer_id)
        self.conn.commit()
        self._audit("review", "protocol", protocol_id, detail=decision, user_id=reviewer_id)
        return rev_id

    def get_reviews(self, protocol_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT r.*, u.name as reviewer_name FROM reviews r JOIN users u ON r.reviewer_id=u.id WHERE r.protocol_id=? ORDER BY r.decided_at DESC",
            (protocol_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Uploads ───────────────────────────────────────────────────────

    def create_upload(self, filename: str, file_type: str, file_size: int, uploaded_by: str = "") -> str:
        up_id = _uid("up-")
        self.conn.execute(
            "INSERT INTO uploads (id,filename,file_type,file_size,extraction_status,uploaded_by,uploaded_at) VALUES (?,?,?,?,?,?,?)",
            (up_id, filename, file_type, file_size, "pending", uploaded_by or None, _now()),
        )
        self.conn.commit()
        return up_id

    def update_upload_extraction(self, upload_id: str, status: str, extracted_schema: dict = None):
        self.conn.execute(
            "UPDATE uploads SET extraction_status=?, extracted_schema=? WHERE id=?",
            (status, json.dumps(extracted_schema or {}), upload_id),
        )
        self.conn.commit()

    def get_upload(self, upload_id: str) -> Optional[dict]:
        row = self.conn.execute("SELECT * FROM uploads WHERE id=?", (upload_id,)).fetchone()
        if row:
            d = dict(row)
            d["extracted_schema"] = json.loads(d["extracted_schema"]) if d.get("extracted_schema") else {}
            return d
        return None

    # ── Audit ─────────────────────────────────────────────────────────

    def _audit(self, action: str, resource_type: str, resource_id: str = "", detail: str = "", user_id: str = ""):
        self.conn.execute(
            "INSERT INTO audit_log (id,user_id,action,resource_type,resource_id,detail,timestamp) VALUES (?,?,?,?,?,?,?)",
            (_uid("aud-"), user_id or None, action, resource_type, resource_id, detail, _now()),
        )

    def get_audit_log(self, resource_type: str = "", resource_id: str = "", limit: int = 50) -> list[dict]:
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        if resource_type:
            query += " AND resource_type=?"
            params.append(resource_type)
        if resource_id:
            query += " AND resource_id=?"
            params.append(resource_id)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        return [dict(r) for r in self.conn.execute(query, params).fetchall()]

    # ── Stats ─────────────────────────────────────────────────────────

    def stats(self) -> dict:
        return {
            "users": self.conn.execute("SELECT COUNT(*) FROM users").fetchone()[0],
            "protocols": self.conn.execute("SELECT COUNT(*) FROM protocols").fetchone()[0],
            "evidence": self.conn.execute("SELECT COUNT(*) FROM evidence").fetchone()[0],
            "reviews": self.conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0],
            "uploads": self.conn.execute("SELECT COUNT(*) FROM uploads").fetchone()[0],
            "audit_entries": self.conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0],
        }
