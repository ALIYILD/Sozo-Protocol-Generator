"""Initial schema — all core Sozo tables.

Revision ID: 001
Revises: None
Create Date: 2026-04-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ── Enum types ──────────────────────────────────────────────────────

user_role_enum = postgresql.ENUM(
    "admin", "clinician", "researcher", "readonly",
    name="user_role",
    create_type=False,
)

protocol_version_status_enum = postgresql.ENUM(
    "draft", "needs_review", "approved", "rejected", "exported", "flagged",
    name="protocol_version_status",
    create_type=False,
)

generation_method_enum = postgresql.ENUM(
    "manual", "ai_generated", "template_derived", "hybrid",
    name="generation_method",
    create_type=False,
)

review_status_enum = postgresql.ENUM(
    "draft", "needs_review", "approved", "rejected", "exported", "flagged",
    name="review_status",
    create_type=False,
)


def upgrade() -> None:
    # ── Create enum types ───────────────────────────────────────────
    op.execute("CREATE TYPE user_role AS ENUM ('admin','clinician','researcher','readonly')")
    op.execute(
        "CREATE TYPE protocol_version_status AS ENUM "
        "('draft','needs_review','approved','rejected','exported','flagged')"
    )
    op.execute(
        "CREATE TYPE generation_method AS ENUM "
        "('manual','ai_generated','template_derived','hybrid')"
    )
    op.execute(
        "CREATE TYPE review_status AS ENUM "
        "('draft','needs_review','approved','rejected','exported','flagged')"
    )

    # ── users ───────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("role", user_role_enum, nullable=False, server_default="clinician"),
        sa.Column("credentials_hash", sa.String(512), nullable=True),
        sa.Column("organization_id", sa.String(128), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # ── protocols ───────────────────────────────────────────────────
    op.create_table(
        "protocols",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("condition_slug", sa.String(128), nullable=False, index=True),
        sa.Column("primary_modality", sa.String(64), nullable=False),
        sa.Column("is_template", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── protocol_versions ───────────────────────────────────────────
    op.create_table(
        "protocol_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("protocol_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("protocols.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", protocol_version_status_enum, nullable=False, server_default="draft"),
        sa.Column("data", postgresql.JSONB(), nullable=True),
        sa.Column("parent_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("build_id", sa.String(128), nullable=True),
        sa.Column("generation_method", generation_method_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.UniqueConstraint("protocol_id", "version_number", name="uq_protocol_version_number"),
    )

    # Add FK from protocols.current_version_id -> protocol_versions.id
    # (deferred because protocol_versions didn't exist when protocols was created)
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
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_metadata", postgresql.JSONB(), nullable=True),
    )

    # ── protocol_evidence ───────────────────────────────────────────
    op.create_table(
        "protocol_evidence",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("protocol_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("protocol_versions.id", ondelete="CASCADE"), nullable=False),
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
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("external_id", sa.String(256), nullable=True),
        sa.Column("demographics", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("organization_id", sa.String(128), nullable=True),
    )

    # ── assessments ─────────────────────────────────────────────────
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("protocol_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("protocols.id", ondelete="SET NULL"), nullable=True),
        sa.Column("scale_name", sa.String(128), nullable=False),
        sa.Column("abbreviation", sa.String(32), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("subscale_scores", postgresql.JSONB(), nullable=True),
        sa.Column("severity_band", sa.String(32), nullable=True),
        sa.Column("assessed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("assessed_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("session_number", sa.Integer(), nullable=True),
    )

    # ── treatment_records ───────────────────────────────────────────
    op.create_table(
        "treatment_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("modality", sa.String(64), nullable=False),
        sa.Column("target", sa.String(128), nullable=True),
        sa.Column("parameters", postgresql.JSONB(), nullable=True),
        sa.Column("sessions_completed", sa.Integer(), nullable=True),
        sa.Column("outcome", sa.String(64), nullable=True),
        sa.Column("outcome_measures", postgresql.JSONB(), nullable=True),
        sa.Column("adverse_events", postgresql.JSONB(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
    )

    # ── medications ─────────────────────────────────────────────────
    op.create_table(
        "medications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("drug_class", sa.String(128), nullable=True),
        sa.Column("dose", sa.String(128), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("interaction_flags", postgresql.JSONB(), nullable=True),
    )

    # ── eeg_records ─────────────────────────────────────────────────
    op.create_table(
        "eeg_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("montage", sa.String(64), nullable=True),
        sa.Column("band_powers", postgresql.JSONB(), nullable=True),
        sa.Column("asymmetry_indices", postgresql.JSONB(), nullable=True),
        sa.Column("peak_alpha_frequency", sa.Float(), nullable=True),
        sa.Column("z_scores", postgresql.JSONB(), nullable=True),
        sa.Column("connectivity", postgresql.JSONB(), nullable=True),
        sa.Column("source_localization", postgresql.JSONB(), nullable=True),
        sa.Column("source_file_path", sa.String(1024), nullable=True),
        sa.Column("processing_params", postgresql.JSONB(), nullable=True),
    )

    # ── reviews ─────────────────────────────────────────────────────
    op.create_table(
        "reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("protocol_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("protocol_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", review_status_enum, nullable=False),
        sa.Column("comments", postgresql.JSONB(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("signature_hash", sa.String(256), nullable=True),
    )

    # ── treatment_sessions ──────────────────────────────────────────
    op.create_table(
        "treatment_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("patient_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("protocol_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("protocol_versions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("session_number", sa.Integer(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("parameters_used", postgresql.JSONB(), nullable=True),
        sa.Column("side_effects", postgresql.JSONB(), nullable=True),
        sa.Column("clinician_notes", sa.Text(), nullable=True),
        sa.Column("outcome_measures", postgresql.JSONB(), nullable=True),
        sa.Column("conducted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── audit_log ───────────────────────────────────────────────────
    op.create_table(
        "audit_log",
        sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(128), nullable=False),
        sa.Column("entity_id", sa.String(128), nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("input_hash", sa.String(256), nullable=True),
        sa.Column("output_hash", sa.String(256), nullable=True),
        sa.Column("node_name", sa.String(128), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
    )

    # ── Composite indexes ───────────────────────────────────────────
    op.create_index("ix_protocol_versions_protocol_status", "protocol_versions", ["protocol_id", "status"])
    op.create_index("ix_evidence_articles_year_level", "evidence_articles", ["year", "evidence_level"])
    op.create_index("ix_patients_external_org", "patients", ["external_id", "organization_id"])
    op.create_index("ix_assessments_patient_scale", "assessments", ["patient_id", "scale_name"])
    op.create_index("ix_audit_log_entity_ts", "audit_log", ["entity_type", "entity_id", "timestamp"])
    op.create_index("ix_treatment_sessions_patient_pv", "treatment_sessions", ["patient_id", "protocol_version_id"])


def downgrade() -> None:
    # ── Drop indexes ────────────────────────────────────────────────
    op.drop_index("ix_treatment_sessions_patient_pv", table_name="treatment_sessions")
    op.drop_index("ix_audit_log_entity_ts", table_name="audit_log")
    op.drop_index("ix_assessments_patient_scale", table_name="assessments")
    op.drop_index("ix_patients_external_org", table_name="patients")
    op.drop_index("ix_evidence_articles_year_level", table_name="evidence_articles")
    op.drop_index("ix_protocol_versions_protocol_status", table_name="protocol_versions")

    # ── Drop tables (reverse dependency order) ──────────────────────
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

    # Drop FK from protocols before dropping protocol_versions
    op.drop_constraint("fk_protocols_current_version", "protocols", type_="foreignkey")
    op.drop_table("protocol_versions")
    op.drop_table("protocols")
    op.drop_table("users")

    # ── Drop enum types ─────────────────────────────────────────────
    op.execute("DROP TYPE IF EXISTS review_status")
    op.execute("DROP TYPE IF EXISTS generation_method")
    op.execute("DROP TYPE IF EXISTS protocol_version_status")
    op.execute("DROP TYPE IF EXISTS user_role")
