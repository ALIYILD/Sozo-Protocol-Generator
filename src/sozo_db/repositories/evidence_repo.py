"""Evidence repository with PMID lookup and bulk upsert."""
from __future__ import annotations

import uuid
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..repository import BaseRepository
from ..models.evidence import EvidenceArticle, ProtocolEvidence


class EvidenceRepository(BaseRepository[EvidenceArticle]):
    model = EvidenceArticle

    # ── Lookups ───────────────────────────────────────────────────────

    async def get_by_pmid(self, pmid: str) -> EvidenceArticle | None:
        return await self.session.get(EvidenceArticle, pmid)

    async def get_many_by_pmids(self, pmids: list[str]) -> Sequence[EvidenceArticle]:
        if not pmids:
            return []
        stmt = select(EvidenceArticle).where(EvidenceArticle.pmid.in_(pmids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_doi(self, doi: str) -> EvidenceArticle | None:
        stmt = select(EvidenceArticle).where(EvidenceArticle.doi == doi)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search_by_title(
        self, query: str, *, limit: int = 20
    ) -> Sequence[EvidenceArticle]:
        stmt = (
            select(EvidenceArticle)
            .where(EvidenceArticle.title.ilike(f"%{query}%"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ── Bulk upsert (PostgreSQL) ──────────────────────────────────────

    async def bulk_upsert(self, articles: list[dict[str, Any]]) -> int:
        """
        Insert or update articles by PMID. Returns the number of rows affected.

        Each dict must contain at least ``pmid`` and ``title``.
        Uses PostgreSQL ON CONFLICT DO UPDATE. Falls back to merge for
        non-PostgreSQL backends.
        """
        if not articles:
            return 0

        dialect = self.session.bind.dialect.name if self.session.bind else ""  # type: ignore[union-attr]

        if dialect == "postgresql":
            stmt = pg_insert(EvidenceArticle).values(articles)
            update_cols = {
                c.name: c
                for c in stmt.excluded
                if c.name != "pmid"
            }
            stmt = stmt.on_conflict_do_update(
                index_elements=["pmid"],
                set_=update_cols,
            )
            result = await self.session.execute(stmt)
            await self.session.flush()
            return result.rowcount  # type: ignore[return-value]
        else:
            # Fallback: merge one-by-one (SQLite, etc.)
            count = 0
            for data in articles:
                obj = EvidenceArticle(**data)
                merged = await self.session.merge(obj)
                count += 1
            await self.session.flush()
            return count

    # ── Protocol-evidence links ───────────────────────────────────────

    async def link_to_version(
        self,
        protocol_version_id: uuid.UUID,
        pmid: str,
        *,
        section_slug: str | None = None,
        relevance_score: float | None = None,
        claim_text: str | None = None,
        claim_category: str | None = None,
        confidence: str | None = None,
    ) -> ProtocolEvidence:
        link = ProtocolEvidence(
            protocol_version_id=protocol_version_id,
            pmid=pmid,
            section_slug=section_slug,
            relevance_score=relevance_score,
            claim_text=claim_text,
            claim_category=claim_category,
            confidence=confidence,
        )
        self.session.add(link)
        await self.session.flush()
        return link

    async def list_for_version(
        self, protocol_version_id: uuid.UUID
    ) -> Sequence[ProtocolEvidence]:
        stmt = (
            select(ProtocolEvidence)
            .where(ProtocolEvidence.protocol_version_id == protocol_version_id)
            .order_by(ProtocolEvidence.relevance_score.desc().nullslast())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
