"""Audit repository — append-only, no update or delete."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..repository import BaseRepository
from ..models.audit import AuditEvent


class AuditRepository(BaseRepository[AuditEvent]):
    model = AuditEvent

    # ── Disabled mutations ────────────────────────────────────────────

    async def update(self, obj: AuditEvent, **values: Any) -> AuditEvent:
        raise NotImplementedError("Audit events are append-only; updates are forbidden.")

    async def delete(self, obj: AuditEvent) -> None:
        raise NotImplementedError("Audit events are append-only; deletes are forbidden.")

    async def delete_by_id(self, id_: Any) -> bool:
        raise NotImplementedError("Audit events are append-only; deletes are forbidden.")

    # ── Append ────────────────────────────────────────────────────────

    async def log(
        self,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_id: uuid.UUID | None = None,
        input_hash: str | None = None,
        output_hash: str | None = None,
        node_name: str | None = None,
        details: dict | None = None,
    ) -> AuditEvent:
        """Convenience method to create an audit event."""
        event = AuditEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor_id=actor_id,
            input_hash=input_hash,
            output_hash=output_hash,
            node_name=node_name,
            details=details,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    # ── Queries ───────────────────────────────────────────────────────

    async def list_for_entity(
        self,
        entity_type: str,
        entity_id: str,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditEvent]:
        stmt = (
            select(AuditEvent)
            .where(
                AuditEvent.entity_type == entity_type,
                AuditEvent.entity_id == entity_id,
            )
            .order_by(AuditEvent.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_actor(
        self,
        actor_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditEvent]:
        stmt = (
            select(AuditEvent)
            .where(AuditEvent.actor_id == actor_id)
            .order_by(AuditEvent.timestamp.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_action(
        self,
        action: str,
        *,
        since: datetime | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[AuditEvent]:
        stmt = select(AuditEvent).where(AuditEvent.action == action)
        if since is not None:
            stmt = stmt.where(AuditEvent.timestamp >= since)
        stmt = stmt.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
