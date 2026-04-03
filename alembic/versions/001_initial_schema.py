"""Initial schema — all core Sozo tables.

Revision ID: 001
Revises: None
Create Date: 2026-04-03

Supports both PostgreSQL (production) and SQLite (development).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    """Detect if running against SQLite."""
    return op.get_bind().dialect.name == "sqlite"


def _uuid_col(name: str, **kwargs) -> sa.Column:
    """UUID column — CHAR(36) on SQLite, native UUID on PostgreSQL."""
    return sa.Column(name, sa.String(36), **kwargs)


def _jsonb_col(name: str, **kwargs) -> sa.Column:
    """JSONB column — TEXT on SQLite, JSONB on PostgreSQL."""
    if _is_sqlite():
        return sa.Column(name, sa.Text(), **kwargs)
    from sqlalchemy.dialects.postgresql import JSONB
    return sa.Column(name, JSONB(), **kwargs)


def _now_default():
    """Server default for current timestamp."""
    if _is_sqlite():
        return sa.text("(datetime('now'))")
    return sa.func.now()


def _uuid_default():
    """Server default for UUID generation."""
    if _is_sqlite():
        return None  # App generates UUIDs
    return sa.text("gen_random_uuid()")


def _bool_default(val: bool):
    if _is_sqlite():
        return sa.text("1" if val else "0")
    return sa.text("true" if val else "false")


def upgrade() -> None:
    sqlite = _is_sqlite()

    # PostgreSQL: create enum types
    if not sqlite:
        op.execute("CREATE TYPE user_role AS ENUM ('admin','clinician','reviewer','operator','readonly')")
        op.execute(
            "CREATE TYPE protocol_version_status AS ENUM "
            "('draft','pending_review','approved','rejected','superseded','archived')"
        )
        op.execute(
            "CREATE TYPE generation_method AS ENUM "
            "('condition_based','template_extracted','prompt_generated','personalized','manual')"
        )
        op.execute(
            "CREATE TYPE review_status AS ENUM "
            "('pending','approved','rejected','revision_requested')"
        )

    # ── users ───────────────────────────────────────────────────────
    cols = [
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="clinician"),
        sa.Column("credentials_hash", sa.String(512), nullable=True),
        sa.Column("organization_id", sa.String(128), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=_bool_default(True)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=_now_default()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=_now_default()),
    ]
    op.create_table("users", *cols)

    # ── protocols ───────────────────────────────────────────────────
    op.create_table(
        "protocols",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("current_version_id", sa.String(36), nullable=True),
        sa.Column("condition_slug", sa.String(128), nullable=False, index=True),
        sa.Column("primary_modality", sa.String(64), nullable=False),
        sa.Column("is_template", sa.Boolean(), nullable=False, server_default=_bool_default(False)),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=_now_default()),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── protocol_versions ───────────────────────────────────────────
    op.create_table(
        "protocol_versions",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("protocol_id", sa.String(36), sa.ForeignKey("protocols.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="draft"),
        _jsonb_col("data", nullable=True),
        sa.Column("parent_version_id", sa.String(36), nullable=True),
        sa.Column("build_id", sa.String(128), nullable=True),
        sa.Column("generation_method", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=_now_default()),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("protocol_id", "version_number", name="uq_protocol_version_number"),
    )

    # Deferred FK: protocols.current_version_id → protocol_versions.id
    if not sqlite:
        op.create_foreign_key(
            "fk_protocols_current_version",
            "protocols", "protocol_versions",
            ["current_version_id"], ["id"],
            ondelete="SET NULL",
        )

    # ── evidence_articles ───────────────────────────────────────────
    op.create_table(
        "evidence_articles",
        sa.Column("pmid", sa.String(32), primary_key=True),
        sa.Column("doi", sa.String(256), nullable=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("authors", sa.Text(), nullable=True),
        sa.Column("journal", sa.String(512), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("abstract", sa.Text(), nullable=True),
        sa.Column("evidence_type", sa.String(64), nullable=True),
        sa.Column("evidence_level", sa.String(32), nullable=True),
        sa.Column("composite_score", sa.Float(), nullable=True),
        sa.Column("source", sa.String(64), nullable=True),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default=_bool_default(False)),
        sa.Column("fetched_at", sa.DateTime(), nullable=True),
        _jsonb_col("raw_metadata", nullable=True),
    )

    # ── protocol_evidence ───────────────────────────────────────────
    op.create_table(
        "protocol_evidence",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("protocol_version_id", sa.String(36), sa.ForeignKey("protocol_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("pmid", sa.String(32), sa.ForeignKey("evidence_articles.pmid", ondelete="CASCADE"), nullable=False),
        sa.Column("section_slug", sa.String(128), nullable=True),
        sa.Column("relevance_score", sa.Float(), nullable=True),
        sa.Column("claim_text", sa.Text(), nullable=True),
        sa.Column("claim_category", sa.String(64), nullable=True),
        sa.Column("confidence", sa.String(32), nullable=True),
    )

    # ── patients ────────────────────────────────────────────────────
    op.create_table(
        "patients",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("external_id", sa.String(256), nullable=True),
        _jsonb_col("demographics", nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=_now_default()),
        sa.Column("created_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("organization_id", sa.String(128), nullable=True),
    )

    # ── assessments ─────────────────────────────────────────────────
    op.create_table(
        "assessments",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("protocol_id", sa.String(36), sa.ForeignKey("protocols.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scale_name", sa.String(128), nullable=False),
        sa.Column("abbreviation", sa.String(32), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        _jsonb_col("subscale_scores", nullable=True),
        sa.Column("severity_band", sa.String(32), nullable=True),
        sa.Column("assessed_at", sa.DateTime(), nullable=False),
        sa.Column("assessed_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_number", sa.Integer(), nullable=True),
    )

    # ── treatment_records ───────────────────────────────────────────
    op.create_table(
        "treatment_records",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("modality", sa.String(64), nullable=False),
        sa.Column("target", sa.String(128), nullable=True),
        _jsonb_col("parameters", nullable=True),
        sa.Column("sessions_completed", sa.Integer(), nullable=True),
        sa.Column("outcome", sa.String(64), nullable=True),
        _jsonb_col("outcome_measures", nullable=True),
        _jsonb_col("adverse_events", nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
    )

    # ── medications ─────────────────────────────────────────────────
    op.create_table(
        "medications",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("drug_class", sa.String(128), nullable=True),
        sa.Column("dose", sa.String(128), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        _jsonb_col("interaction_flags", nullable=True),
    )

    # ── eeg_records ─────────────────────────────────────────────────
    op.create_table(
        "eeg_records",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("montage", sa.String(64), nullable=True),
        _jsonb_col("band_powers", nullable=True),
        _jsonb_col("asymmetry_indices", nullable=True),
        sa.Column("peak_alpha_frequency", sa.Float(), nullable=True),
        _jsonb_col("z_scores", nullable=True),
        _jsonb_col("connectivity", nullable=True),
        _jsonb_col("source_localization", nullable=True),
        sa.Column("source_file_path", sa.String(1024), nullable=True),
        _jsonb_col("processing_params", nullable=True),
    )

    # ── reviews ─────────────────────────────────────────────────────
    op.create_table(
        "reviews",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("protocol_version_id", sa.String(36), sa.ForeignKey("protocol_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        _jsonb_col("comments", nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=False),
        sa.Column("signature_hash", sa.String(256), nullable=True),
    )

    # ── treatment_sessions ──────────────────────────────────────────
    op.create_table(
        "treatment_sessions",
        _uuid_col("id", primary_key=True, server_default=_uuid_default()),
        sa.Column("patient_id", sa.String(36), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("protocol_version_id", sa.String(36), sa.ForeignKey("protocol_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_number", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        _jsonb_col("parameters_used", nullable=True),
        _jsonb_col("side_effects", nullable=True),
        sa.Column("clinician_notes", sa.Text(), nullable=True),
        _jsonb_col("outcome_measures", nullable=True),
        sa.Column("conducted_by", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── audit_log ───────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger().with_variant(sa.Integer(), "sqlite"), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(128), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False, server_default=_now_default()),
        sa.Column("input_hash", sa.String(256), nullable=True),
        sa.Column("output_hash", sa.String(256), nullable=True),
        sa.Column("node_name", sa.String(128), nullable=True),
        _jsonb_col("details", nullable=True),
    )

    # ── Composite indexes ───────────────────────────────────────────
    op.create_index("ix_protocol_versions_protocol_status", "protocol_versions", ["protocol_id", "status"])
    op.create_index("ix_evidence_articles_year_level", "evidence_articles", ["year", "evidence_level"])
    op.create_index("ix_patients_external_org", "patients", ["external_id", "organization_id"])
    op.create_index("ix_assessments_patient_scale", "assessments", ["patient_id", "scale_name"])
    op.create_index("ix_audit_log_entity_ts", "audit_log", ["entity_type", "entity_id", "timestamp"])
    op.create_index("ix_treatment_sessions_patient_pv", "treatment_sessions", ["patient_id", "protocol_version_id"])


def downgrade() -> None:
    sqlite = _is_sqlite()

    # Drop indexes
    op.drop_index("ix_treatment_sessions_patient_pv", table_name="treatment_sessions")
    op.drop_index("ix_audit_log_entity_ts", table_name="audit_log")
    op.drop_index("ix_assessments_patient_scale", table_name="assessments")
    op.drop_index("ix_patients_external_org", table_name="patients")
    op.drop_index("ix_evidence_articles_year_level", table_name="evidence_articles")
    op.drop_index("ix_protocol_versions_protocol_status", table_name="protocol_versions")

    # Drop tables (reverse dependency order)
    op.drop_table("audit_log")
    op.drop_table("treatment_sessions")
    op.drop_table("reviews")
    op.drop_table("eeg_records")
    op.drop_table("medications")
    op.drop_table("treatment_records")
    op.drop_table("assessments")
    op.drop_table("patients")
    op.drop_table("protocol_evidence")
    op.drop_table("evidence_articles")

    if not sqlite:
        op.drop_constraint("fk_protocols_current_version", "protocols", type_="foreignkey")
    op.drop_table("protocol_versions")
    op.drop_table("protocols")
    op.drop_table("users")

    # PostgreSQL: drop enum types
    if not sqlite:
        op.execute("DROP TYPE IF EXISTS review_status")
        op.execute("DROP TYPE IF EXISTS generation_method")
        op.execute("DROP TYPE IF EXISTS protocol_version_status")
        op.execute("DROP TYPE IF EXISTS user_role")
