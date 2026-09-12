"""Pure helpers that turn stored fields into the display labels the UI shows."""
from __future__ import annotations

from datetime import datetime, timezone

from .models import AccessTask

STATUS_DISPLAY = {
    "pending": "Pending",
    "awaiting_approval": "Awaiting approval",
    "escalated": "Escalated",
    "provisioned": "Provisioned",
    "blocked": "Blocked",
}


def last_nudge_label(task: AccessTask) -> str:
    if task.nudge_count <= 0:
        return "—"
    unit = "nudge" if task.nudge_count == 1 else "nudges"
    label = f"{task.nudge_count} {unit}"
    if task.escalated:
        label += ", escalated"
    return label


def waiting_label(task: AccessTask) -> str:
    requested = task.requested_at
    if requested.tzinfo is None:
        requested = requested.replace(tzinfo=timezone.utc)
    days = (datetime.now(timezone.utc) - requested).days
    if days <= 0:
        return "Waiting today"
    if days == 1:
        return "Waiting 1 day"
    return f"Waiting {days} days"
