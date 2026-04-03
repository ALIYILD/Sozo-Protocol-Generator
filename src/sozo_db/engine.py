"""
SQLAlchemy async engine setup, session factory, and connection pooling.

Uses DATABASE_URL env var with fallback to a local SQLite file for dev.
"""
from __future__ import annotations

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_DEFAULT_DEV_URL = "sqlite+aiosqlite:///./sozo_dev.db"


def _resolve_url() -> str:
    url = os.environ.get("DATABASE_URL", _DEFAULT_DEV_URL)
    # Heroku-style postgres:// → postgresql+asyncpg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def build_engine(url: str | None = None, *, echo: bool = False) -> AsyncEngine:
    """Create an async engine with sensible pool defaults for PostgreSQL."""
    resolved = url or _resolve_url()
    is_sqlite = resolved.startswith("sqlite")

    kwargs: dict = {
        "echo": echo,
        "future": True,
    }

    if not is_sqlite:
        kwargs.update(
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )

    return create_async_engine(resolved, **kwargs)


# ---------------------------------------------------------------------------
# Module-level singletons (lazy)
# ---------------------------------------------------------------------------
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine(*, echo: bool = False) -> AsyncEngine:
    """Return (and cache) the default async engine."""
    global _engine
    if _engine is None:
        _engine = build_engine(echo=echo)
    return _engine


def get_session_factory(*, echo: bool = False) -> async_sessionmaker[AsyncSession]:
    """Return (and cache) the default session factory."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(echo=echo),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency-injection helper (FastAPI, etc.). Yields an async session."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    """Dispose the cached engine (call on app shutdown)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None
