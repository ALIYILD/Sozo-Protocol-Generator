"""Generic async repository base class with CRUD operations (SQLAlchemy 2.0 style)."""
from __future__ import annotations

import uuid
from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import select, func, delete as sa_delete
from sqlalchemy.ext.asyncio import AsyncSession

from .base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async CRUD repository.

    Subclass and set ``model`` to the ORM class. Override methods for
    domain-specific behaviour (e.g. append-only audit log).
    """

    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── Read ──────────────────────────────────────────────────────────

    async def get_by_id(self, id_: Any) -> ModelT | None:
        """Fetch a single record by primary key."""
        return await self.session.get(self.model, id_)

    async def list_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
        order_by: Any | None = None,
        filters: list[Any] | None = None,
    ) -> Sequence[ModelT]:
        """Return a paginated list of records, optionally filtered/ordered."""
        stmt = select(self.model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, *, filters: list[Any] | None = None) -> int:
        """Return total count, optionally filtered."""
        stmt = select(func.count()).select_from(self.model)
        if filters:
            for f in filters:
                stmt = stmt.where(f)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    # ── Write ─────────────────────────────────────────────────────────

    async def create(self, obj: ModelT) -> ModelT:
        """Add a new record and flush to get the generated PK."""
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def create_many(self, objs: Sequence[ModelT]) -> Sequence[ModelT]:
        """Bulk insert."""
        self.session.add_all(objs)
        await self.session.flush()
        return objs

    async def update(self, obj: ModelT, **values: Any) -> ModelT:
        """Update attributes on an existing managed instance."""
        for key, val in values.items():
            setattr(obj, key, val)
        await self.session.flush()
        return obj

    async def delete(self, obj: ModelT) -> None:
        """Delete a single managed instance."""
        await self.session.delete(obj)
        await self.session.flush()

    async def delete_by_id(self, id_: Any) -> bool:
        """Delete by primary key. Returns True if a row was deleted."""
        obj = await self.get_by_id(id_)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
