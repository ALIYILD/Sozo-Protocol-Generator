"""Protocol repository with version management and status transitions."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..repository import BaseRepository
from ..models.protocol import Protocol, ProtocolVersion, VersionStatus


# Valid status transitions: from → set of allowed targets
_TRANSITIONS: dict[VersionStatus, set[VersionStatus]] = {
    VersionStatus.DRAFT: {VersionStatus.PENDING_REVIEW, VersionStatus.ARCHIVED},
    VersionStatus.PENDING_REVIEW: {
        VersionStatus.APPROVED,
        VersionStatus.REJECTED,
        VersionStatus.DRAFT,
    },
    VersionStatus.APPROVED: {VersionStatus.SUPERSEDED, VersionStatus.ARCHIVED},
    VersionStatus.REJECTED: {VersionStatus.DRAFT, VersionStatus.ARCHIVED},
    VersionStatus.SUPERSEDED: set(),
    VersionStatus.ARCHIVED: set(),
}


class ProtocolRepository(BaseRepository[Protocol]):
    model = Protocol

    # ── Queries ───────────────────────────────────────────────────────

    async def get_with_versions(self, protocol_id: uuid.UUID) -> Protocol | None:
        stmt = (
            select(Protocol)
            .options(selectinload(Protocol.versions))
            .where(Protocol.id == protocol_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_condition(
        self, condition_slug: str, *, offset: int = 0, limit: int = 50
    ) -> Sequence[Protocol]:
        stmt = (
            select(Protocol)
            .where(Protocol.condition_slug == condition_slug)
            .order_by(Protocol.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_templates(self, *, offset: int = 0, limit: int = 50) -> Sequence[Protocol]:
        stmt = (
            select(Protocol)
            .where(Protocol.is_template.is_(True))
            .order_by(Protocol.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    # ── Version management ────────────────────────────────────────────

    async def create_version(
        self,
        protocol_id: uuid.UUID,
        data: dict,
        *,
        created_by: uuid.UUID | None = None,
        generation_method: str | None = None,
        build_id: str | None = None,
        parent_version_id: uuid.UUID | None = None,
    ) -> ProtocolVersion:
        """Create a new version for a protocol, auto-incrementing version_number."""
        # Determine next version number
        stmt = (
            select(ProtocolVersion.version_number)
            .where(ProtocolVersion.protocol_id == protocol_id)
            .order_by(ProtocolVersion.version_number.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        last = result.scalar_one_or_none()
        next_version = (last or 0) + 1

        version = ProtocolVersion(
            protocol_id=protocol_id,
            version_number=next_version,
            status=VersionStatus.DRAFT,
            data=data,
            parent_version_id=parent_version_id,
            build_id=build_id,
            generation_method=generation_method,
            created_by=created_by,
        )
        self.session.add(version)
        await self.session.flush()
        return version

    async def transition_status(
        self,
        version_id: uuid.UUID,
        target_status: VersionStatus,
        *,
        actor_id: uuid.UUID | None = None,
        review_notes: str | None = None,
    ) -> ProtocolVersion:
        """
        Move a protocol version to a new status.

        Raises ValueError if the transition is invalid.
        When approving, sets approved_by/approved_at and updates the
        parent protocol's current_version_id.
        """
        version = await self.session.get(ProtocolVersion, version_id)
        if version is None:
            raise ValueError(f"ProtocolVersion {version_id} not found")

        allowed = _TRANSITIONS.get(version.status, set())
        if target_status not in allowed:
            raise ValueError(
                f"Cannot transition from {version.status.value} to {target_status.value}. "
                f"Allowed: {[s.value for s in allowed]}"
            )

        version.status = target_status
        if review_notes is not None:
            version.review_notes = review_notes

        if target_status == VersionStatus.APPROVED:
            version.approved_by = actor_id
            version.approved_at = datetime.now(timezone.utc)
            # Supersede the previous current version
            protocol = await self.session.get(Protocol, version.protocol_id)
            if protocol is not None:
                if (
                    protocol.current_version_id is not None
                    and protocol.current_version_id != version_id
                ):
                    prev = await self.session.get(ProtocolVersion, protocol.current_version_id)
                    if prev is not None and prev.status == VersionStatus.APPROVED:
                        prev.status = VersionStatus.SUPERSEDED
                protocol.current_version_id = version_id

        await self.session.flush()
        return version

    async def get_version(self, version_id: uuid.UUID) -> ProtocolVersion | None:
        return await self.session.get(ProtocolVersion, version_id)

    async def list_versions(
        self, protocol_id: uuid.UUID, *, status: VersionStatus | None = None
    ) -> Sequence[ProtocolVersion]:
        stmt = (
            select(ProtocolVersion)
            .where(ProtocolVersion.protocol_id == protocol_id)
        )
        if status is not None:
            stmt = stmt.where(ProtocolVersion.status == status)
        stmt = stmt.order_by(ProtocolVersion.version_number.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
