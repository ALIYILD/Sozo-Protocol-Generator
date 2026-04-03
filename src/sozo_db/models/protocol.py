"""Protocol and ProtocolVersion models."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, UUIDMixin, TimestampMixin


class VersionStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class GenerationMethod(str, enum.Enum):
    AUTOMATED = "automated"
    MANUAL = "manual"
    HYBRID = "hybrid"
    IMPORTED = "imported"


class Protocol(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "protocols"

    current_version_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("protocol_versions.id", use_alter=True, name="fk_protocol_current_version"),
        nullable=True,
    )
    condition_slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    primary_modality: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    creator: Mapped["User"] = relationship(  # noqa: F821
        "User", back_populates="protocols_created", foreign_keys=[created_by]
    )
    versions: Mapped[list["ProtocolVersion"]] = relationship(
        "ProtocolVersion",
        back_populates="protocol",
        foreign_keys="ProtocolVersion.protocol_id",
        cascade="all, delete-orphan",
        order_by="ProtocolVersion.version_number.desc()",
    )
    current_version: Mapped["ProtocolVersion | None"] = relationship(
        "ProtocolVersion",
        foreign_keys=[current_version_id],
        post_update=True,
        uselist=False,
    )

    __table_args__ = (
        Index("ix_protocols_condition_template", "condition_slug", "is_template"),
    )

    def __repr__(self) -> str:
        return f"<Protocol {self.id} condition={self.condition_slug}>"


class ProtocolVersion(UUIDMixin, Base):
    __tablename__ = "protocol_versions"

    protocol_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("protocols.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[VersionStatus] = mapped_column(nullable=False, default=VersionStatus.DRAFT)
    data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    parent_version_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("protocol_versions.id"),
        nullable=True,
    )
    build_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    generation_method: Mapped[GenerationMethod | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    protocol: Mapped["Protocol"] = relationship(
        "Protocol", back_populates="versions", foreign_keys=[protocol_id]
    )
    evidence_links: Mapped[list["ProtocolEvidence"]] = relationship(  # noqa: F821
        "ProtocolEvidence", back_populates="protocol_version", cascade="all, delete-orphan"
    )
    reviews: Mapped[list["Review"]] = relationship(  # noqa: F821
        "Review", back_populates="protocol_version", cascade="all, delete-orphan"
    )
    sessions: Mapped[list["TreatmentSession"]] = relationship(  # noqa: F821
        "TreatmentSession", back_populates="protocol_version"
    )

    __table_args__ = (
        Index("ix_pv_protocol_version", "protocol_id", "version_number", unique=True),
        Index("ix_pv_status", "status"),
        Index("ix_pv_build_id", "build_id"),
    )

    def __repr__(self) -> str:
        return f"<ProtocolVersion {self.id} v{self.version_number} status={self.status.value}>"
