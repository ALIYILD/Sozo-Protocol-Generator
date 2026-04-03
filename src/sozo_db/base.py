"""Declarative base and common mixins for all Sozo DB models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """Declarative base for all Sozo models."""
    pass


class UUIDMixin:
    """Provides a UUID primary key column named `id`."""

    @declared_attr.directive
    def id(cls) -> Mapped[uuid.UUID]:
        return mapped_column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            sort_order=-100,
        )


class TimestampMixin:
    """Provides created_at and updated_at columns with server defaults."""

    @declared_attr.directive
    def created_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            sort_order=900,
        )

    @declared_attr.directive
    def updated_at(cls) -> Mapped[datetime]:
        return mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
            sort_order=901,
        )
