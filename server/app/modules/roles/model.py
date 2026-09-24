from datetime import datetime, timezone
from typing import TYPE_CHECKING, Literal

from sqlalchemy import Boolean, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from server.app.core.database.base import Base
from server.app.modules.users.model import user_roles
from server.app.modules.permissions.model import Permission, role_permissions

if TYPE_CHECKING:
    from server.app.modules.users.model import User


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("name", name="uq_roles_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    data_scope: Mapped[Literal["all", "self"]] = mapped_column(String(16), nullable=False, default="all", server_default="all")
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    users: Mapped[list["User"]] = relationship("User", secondary=user_roles, back_populates="roles")
    permissions: Mapped[list[Permission]] = relationship("Permission", secondary=role_permissions, backref="roles")
