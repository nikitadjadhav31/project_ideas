"""Seed the database with the reference onboarding story.

Idempotent: does nothing if hires already exist. Mirrors the data shown in the
design mockup so the app opens in a realistic working state.
"""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from . import models
from .models import utcnow


def seed(db: Session) -> None:
    if db.query(models.Hire).count() > 0:
        return

    now = utcnow()

    arjun = models.Hire(name="Arjun Mehta", department="Engineering", start_label="Mon")
    meera = models.Hire(name="Meera Iyer", department="Product", start_label="Wed")
    db.add_all([arjun, meera])
    db.flush()  # assign ids

    tasks = [
        models.AccessTask(hire_id=arjun.id, tool="GitHub", scope="eng team",
                          status="provisioned", requested_at=now - timedelta(days=3)),
        models.AccessTask(hire_id=arjun.id, tool="GroundCover", scope="standard",
                          approver_name="Priya Nair", approver_email="priya.nair@company.com",
                          status="awaiting_approval", nudge_count=2,
                          requested_at=now - timedelta(days=2)),
        models.AccessTask(hire_id=arjun.id, tool="Databricks", scope="prod write",
                          approver_name="Rohan Desai", approver_email="rohan.desai@company.com",
                          status="escalated", nudge_count=3, escalated=True,
                          sensitive=True, requires_manual=True, step="Step 1 of 2",
                          requested_at=now - timedelta(days=3)),

        models.AccessTask(hire_id=meera.id, tool="Jira", scope="product-pms",
                          status="provisioned", requested_at=now - timedelta(days=1)),
        models.AccessTask(hire_id=meera.id, tool="Figma", scope="editor seat",
                          approver_name="Kavya Rao", approver_email="kavya.rao@company.com",
                          status="awaiting_approval", nudge_count=1,
                          requested_at=now - timedelta(days=1)),
        models.AccessTask(hire_id=meera.id, tool="Databricks", scope="read (common)",
                          approver_name="Rohan Desai", approver_email="rohan.desai@company.com",
                          status="pending", requested_at=now - timedelta(days=1)),
    ]
    db.add_all(tasks)

    # Audit trail telling the onboarding story (oldest first; API returns newest first).
    def ev(mins_ago, actor, is_agent, action, detail, refused=False):
        return models.AuditEvent(
            timestamp=now - timedelta(minutes=mins_ago), actor=actor, is_agent=is_agent,
            action=action, detail=detail, refused=refused,
        )

    db.add_all([
        ev(363, "Suraj Khanna", False, "Hire created",
           "New hire Arjun Mehta (Engineering) submitted via intake form, start Mon."),
        ev(363, "Orchestrator", True, "Tasks fanned out",
           "3 access tasks created for Arjun Mehta and routed to owners."),
        ev(362, "Provisioner", True, "Access granted",
           "GitHub · eng team provisioned automatically for Arjun Mehta."),
        ev(362, "Provisioner", True, "API error",
           "Databricks API returned 503 — automated provisioning failed for prod write."),
        ev(361, "Provisioner", True, "Retry",
           "Databricks provisioning retried after API error (attempt 2 of 3)."),
        ev(359, "Provisioner", True, "Fallback to ticket",
           "Databricks auto-grant unavailable after 3 attempts — routed to approver Rohan Desai."),
        ev(320, "Suraj Khanna", False, "Hire created",
           "New hire Meera Iyer (Product) submitted via intake form, start Wed."),
        ev(319, "Provisioner", True, "Access granted",
           "Jira · product-pms provisioned automatically for Meera Iyer."),
        ev(300, "Follow-up agent", True, "Nudge sent",
           "Reminder to Priya Nair for GroundCover · standard (nudge 1 of 3)."),
        ev(240, "Follow-up agent", True, "Nudge sent",
           "Reminder to Rohan Desai for Databricks · prod write (nudge 1 of 3)."),
        ev(180, "Follow-up agent", True, "Nudge sent",
           "Reminder to Kavya Rao for Figma · editor seat (nudge 1 of 3)."),
        ev(150, "Follow-up agent", True, "Nudge sent",
           "Reminder to Priya Nair for GroundCover · standard (nudge 2 of 3)."),
        ev(90, "Follow-up agent", True, "Nudge sent",
           "Reminder to Rohan Desai for Databricks · prod write (nudge 2 of 3)."),
        ev(25, "Follow-up agent", True, "Escalated",
           "Databricks · prod write for Arjun Mehta escalated to Rohan Desai after nudge 3."),
        ev(5, "Priya Nair", False, "Refused",
           "Reply attempted to approve Databricks · prod write for Arjun Mehta — "
           "not authorised, sender does not own this item.", refused=True),
    ])

    db.commit()
