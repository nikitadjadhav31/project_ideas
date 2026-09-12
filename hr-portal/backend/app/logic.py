"""Interpret a free-text approver reply and apply it to the items they own.

This is the server-side counterpart of the "result strip" on the Approvals
screen: it detects intent, applies the decision to items the sender actually
owns, and refuses items owned by someone else — writing an audit trail for
every outcome.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from . import models, schemas

APPROVE_WORDS = ("approve", "approved", "approving", "grant", "granted", "ok", "okay", "yes", "sign off")
REJECT_WORDS = ("reject", "rejected", "deny", "denied", "decline", "declined", "no")

# States an approver reply can still act on.
OPEN_STATES = ("pending", "awaiting_approval", "escalated")


def detect_intent(text: str) -> str:
    t = text.lower()
    if any(w in t for w in APPROVE_WORDS):
        return "Approve"
    if any(w in t for w in REJECT_WORDS):
        return "Reject"
    return "Unclear"


def _audit(db: Session, *, actor: str, action: str, detail: str, refused: bool = False) -> None:
    db.add(models.AuditEvent(actor=actor, is_agent=False, action=action, detail=detail, refused=refused))


def interpret_reply(db: Session, approver_email: str, text: str) -> schemas.ReplyResult:
    intent = detect_intent(text)
    lower = text.lower()

    # Candidate tasks are open items whose tool name is mentioned in the reply.
    tasks = (
        db.query(models.AccessTask)
        .filter(models.AccessTask.status.in_(OPEN_STATES))
        .all()
    )
    mentioned = [t for t in tasks if t.tool.lower() in lower]

    items: list[schemas.ReplyResultItem] = []
    applied = skipped = 0

    for task in mentioned:
        hire_name = task.hire.name
        owns = (task.approver_email or "").lower() == approver_email.lower()

        if not owns:
            skipped += 1
            items.append(
                schemas.ReplyResultItem(
                    tool=task.tool, scope=task.scope, hire_name=hire_name,
                    outcome="not_authorised",
                    note="Not authorised — you don't own this item.",
                )
            )
            _audit(
                db, actor=approver_email, action="Refused", refused=True,
                detail=f"Reply attempted to approve {task.tool} · {task.scope} for "
                       f"{hire_name} — not authorised, sender does not own this item.",
            )
            continue

        if intent == "Approve":
            task.status = "provisioned"
            task.escalated = False
            applied += 1
            items.append(
                schemas.ReplyResultItem(
                    tool=task.tool, scope=task.scope, hire_name=hire_name,
                    outcome="approved", note="Provisioning started.",
                )
            )
            _audit(db, actor=approver_email, action="Approved",
                   detail=f'Reply "{text.strip()}" — {task.tool} · {task.scope} approved for {hire_name}.')
            db.add(models.AuditEvent(
                actor="Provisioner", is_agent=True, action="Access granted",
                detail=f"{task.tool} · {task.scope} provisioned for {hire_name}.",
            ))
        elif intent == "Reject":
            task.status = "blocked"
            applied += 1
            items.append(
                schemas.ReplyResultItem(
                    tool=task.tool, scope=task.scope, hire_name=hire_name,
                    outcome="rejected", note="Request blocked by approver.",
                )
            )
            _audit(db, actor=approver_email, action="Rejected",
                   detail=f'Reply "{text.strip()}" — {task.tool} · {task.scope} blocked for {hire_name}.')
        else:
            skipped += 1
            items.append(
                schemas.ReplyResultItem(
                    tool=task.tool, scope=task.scope, hire_name=hire_name,
                    outcome="not_authorised",
                    note="Intent unclear — no action taken.",
                )
            )

    db.commit()
    return schemas.ReplyResult(
        intent=intent, applied_count=applied, skipped_count=skipped, items=items
    )
