"""Declarative base and common mixins for all Sozo DB models."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, JSON, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


# Dialect-aware JSON type: JSONB on PostgreSQL (indexable, native),
# JSON (→TEXT) on SQLite. Models should use this instead of importing
# JSONB directly — otherwise Base.metadata.create_all() on SQLite raises
# `CompileError: can't render element of type JSONB` and aborts CREATE
# of every subsequent table in the metadata, which is how the ENTIRE
# DB schema ended up missing `graph_runs`, `reviews`, `treatment_sessions`
# etc. on the Fly deploy today.
JSON_VARIANT = JSON().with_variant(JSONB(), "postgresql")


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
