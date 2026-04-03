"""User model."""
from __future__ import annotations

import enum
import uuid

from sqlalchemy import String, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base, UUIDMixin, TimestampMixin


class UserRole(str, enum.Enum):
    CLINICIAN = "clinician"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    OPERATOR = "operator"


class User(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(nullable=False, default=UserRole.CLINICIAN)
    credentials_hash: Mapped[str | None] = mapped_column(String(512), nullable=True)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True), nullable=True, index=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships (back-populates defined on child side)
    protocols_created: Mapped[list["Protocol"]] = relationship(  # noqa: F821
        "Protocol", back_populates="creator", foreign_keys="Protocol.created_by"
    )

    __table_args__ = (
        Index("ix_users_org_active", "organization_id", "active"),
    )

    def __repr__(self) -> str:
        return f"<User {self.email} role={self.role.value}>"
