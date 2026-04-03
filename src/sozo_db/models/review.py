"""Review model."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, UUIDMixin


class ReviewStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class Review(UUIDMixin, Base):
    __tablename__ = "reviews"

    protocol_version_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("protocol_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    reviewer_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    status: Mapped[ReviewStatus] = mapped_column(nullable=False, default=ReviewStatus.PENDING)
    comments: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signature_hash: Mapped[str | None] = mapped_column(String(256), nullable=True)

    # Relationships
    protocol_version: Mapped["ProtocolVersion"] = relationship(  # noqa: F821
        "ProtocolVersion", back_populates="reviews"
    )

    __table_args__ = (
        Index("ix_reviews_version", "protocol_version_id"),
        Index("ix_reviews_reviewer", "reviewer_id"),
        Index("ix_reviews_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Review {self.id} status={self.status.value}>"
