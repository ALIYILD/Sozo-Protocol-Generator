"""Evidence article and protocol-evidence link models."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base


class EvidenceSource(str, enum.Enum):
    PUBMED = "pubmed"
    CROSSREF = "crossref"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    MANUAL = "manual"
    GUIDELINE = "guideline"
    DEVICE_MANUAL = "device_manual"


class EvidenceArticle(Base):
    __tablename__ = "evidence_articles"

    pmid: Mapped[str] = mapped_column(String(32), primary_key=True)
    doi: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    authors: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    journal: Mapped[str | None] = mapped_column(String(512), nullable=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    abstract: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_level: Mapped[str | None] = mapped_column(String(32), nullable=True)
    composite_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    source: Mapped[EvidenceSource] = mapped_column(
        nullable=False, default=EvidenceSource.PUBMED
    )
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    raw_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    protocol_links: Mapped[list["ProtocolEvidence"]] = relationship(
        "ProtocolEvidence", back_populates="article", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_evidence_source", "source"),
        Index("ix_evidence_level", "evidence_level"),
    )

    def __repr__(self) -> str:
        return f"<EvidenceArticle pmid={self.pmid} title={self.title[:40]}>"


class ProtocolEvidence(Base):
    __tablename__ = "protocol_evidence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    protocol_version_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("protocol_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    pmid: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("evidence_articles.pmid", ondelete="CASCADE"),
        nullable=False,
    )
    section_slug: Mapped[str | None] = mapped_column(String(128), nullable=True)
    relevance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    claim_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_category: Mapped[str | None] = mapped_column(String(64), nullable=True)
    confidence: Mapped[str | None] = mapped_column(String(32), nullable=True)

    # Relationships
    protocol_version: Mapped["ProtocolVersion"] = relationship(  # noqa: F821
        "ProtocolVersion", back_populates="evidence_links"
    )
    article: Mapped["EvidenceArticle"] = relationship(
        "EvidenceArticle", back_populates="protocol_links"
    )

    __table_args__ = (
        Index("ix_pe_version_pmid", "protocol_version_id", "pmid"),
        Index("ix_pe_section", "section_slug"),
    )

    def __repr__(self) -> str:
        return f"<ProtocolEvidence version={self.protocol_version_id} pmid={self.pmid}>"
