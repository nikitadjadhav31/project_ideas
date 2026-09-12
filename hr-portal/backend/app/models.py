"""SQLAlchemy ORM models for the HR Portal domain."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


# Access-task status values shared with the frontend.
STATUSES = ("pending", "awaiting_approval", "escalated", "provisioned", "blocked")


class Hire(Base):
    __tablename__ = "hires"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    start_label: Mapped[str] = mapped_column(String, nullable=False)  # e.g. "Mon"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    tasks: Mapped[list["AccessTask"]] = relationship(
        back_populates="hire", cascade="all, delete-orphan", order_by="AccessTask.id"
    )


class AccessTask(Base):
    __tablename__ = "access_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hire_id: Mapped[int] = mapped_column(ForeignKey("hires.id"), nullable=False)
    tool: Mapped[str] = mapped_column(String, nullable=False)
    scope: Mapped[str] = mapped_column(String, nullable=False)
    approver_name: Mapped[str | None] = mapped_column(String, nullable=True)
    approver_email: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending", nullable=False)
    nudge_count: Mapped[int] = mapped_column(Integer, default=0)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_manual: Mapped[bool] = mapped_column(Boolean, default=False)
    step: Mapped[str | None] = mapped_column(String, nullable=True)  # e.g. "Step 1 of 2"
    requested_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    hire: Mapped["Hire"] = relationship(back_populates="tasks")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
    actor: Mapped[str] = mapped_column(String, nullable=False)
    is_agent: Mapped[bool] = mapped_column(Boolean, default=False)
    action: Mapped[str] = mapped_column(String, nullable=False)
    detail: Mapped[str] = mapped_column(String, nullable=False)
    refused: Mapped[bool] = mapped_column(Boolean, default=False)
