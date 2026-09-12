"""HR Portal API — FastAPI application.

Endpoints back the three SPA screens:
  GET  /api/dashboard   → stats + hires with access tasks
  GET  /api/approvals   → open items grouped per approver
  POST /api/approvals/reply → interpret a free-text approver reply
  GET  /api/audit       → audit events, newest first
  POST /api/hires       → create a hire (Intake form)
"""
from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from . import logic, models, schemas
from .database import Base, SessionLocal, engine, get_db
from .labels import last_nudge_label, waiting_label
from .seed import seed

app = FastAPI(title="HR Portal API", version="1.0.0")

# Vite dev server origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()


def _task_out(task: models.AccessTask) -> schemas.TaskOut:
    return schemas.TaskOut(
        id=task.id, tool=task.tool, scope=task.scope,
        approver_name=task.approver_name, approver_email=task.approver_email,
        status=task.status, nudge_count=task.nudge_count, escalated=task.escalated,
        sensitive=task.sensitive, requires_manual=task.requires_manual, step=task.step,
        last_nudge=last_nudge_label(task), waiting_label=waiting_label(task),
    )


def _initials(name: str) -> str:
    parts = [p for p in name.split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


@app.get("/api/dashboard", response_model=schemas.DashboardOut)
def dashboard(db: Session = Depends(get_db)) -> schemas.DashboardOut:
    hires = db.query(models.Hire).order_by(models.Hire.id).all()
    tasks = db.query(models.AccessTask).all()

    hire_out: list[schemas.HireOut] = []
    for hire in hires:
        total = len(hire.tasks)
        provisioned = sum(1 for t in hire.tasks if t.status == "provisioned")
        readiness = round(provisioned / total * 100) if total else 0
        hire_out.append(schemas.HireOut(
            id=hire.id, name=hire.name, department=hire.department,
            start_label=hire.start_label, readiness=readiness,
            tasks=[_task_out(t) for t in hire.tasks],
        ))

    stats = schemas.Stats(
        active_hires=len(hires),
        awaiting_approval=sum(1 for t in tasks if t.status == "awaiting_approval"),
        escalated=sum(1 for t in tasks if t.status == "escalated"),
    )
    return schemas.DashboardOut(stats=stats, hires=hire_out)


@app.get("/api/approvals", response_model=list[schemas.ApproverRequest])
def approvals(db: Session = Depends(get_db)) -> list[schemas.ApproverRequest]:
    open_tasks = (
        db.query(models.AccessTask)
        .filter(
            models.AccessTask.status.in_(logic.OPEN_STATES),
            models.AccessTask.approver_email.isnot(None),
        )
        .order_by(models.AccessTask.requested_at)
        .all()
    )

    grouped: dict[str, schemas.ApproverRequest] = {}
    for task in open_tasks:
        email = task.approver_email  # not None by filter above
        req = grouped.get(email)
        if req is None:
            req = schemas.ApproverRequest(
                approver_name=task.approver_name or email,
                approver_email=email,
                initials=_initials(task.approver_name or email),
                items=[],
            )
            grouped[email] = req
        req.items.append(schemas.ApprovalItem(
            id=task.id, tool=task.tool, scope=task.scope, hire_name=task.hire.name,
            waiting_label=waiting_label(task), sensitive=task.sensitive,
            requires_manual=task.requires_manual, step=task.step,
        ))
    return list(grouped.values())


@app.post("/api/approvals/reply", response_model=schemas.ReplyResult)
def reply(payload: schemas.ReplyIn, db: Session = Depends(get_db)) -> schemas.ReplyResult:
    return logic.interpret_reply(db, payload.approver_email, payload.text)


@app.get("/api/audit", response_model=list[schemas.AuditOut])
def audit(db: Session = Depends(get_db)) -> list[models.AuditEvent]:
    return (
        db.query(models.AuditEvent)
        .order_by(models.AuditEvent.timestamp.desc(), models.AuditEvent.id.desc())
        .all()
    )


@app.post("/api/hires", response_model=schemas.HireOut, status_code=201)
def create_hire(payload: schemas.HireCreate, db: Session = Depends(get_db)) -> schemas.HireOut:
    hire = models.Hire(
        name=payload.name, department=payload.department, start_label=payload.start_label,
    )
    db.add(hire)
    db.flush()
    db.add(models.AuditEvent(
        actor="Suraj Khanna", is_agent=False, action="Hire created",
        detail=f"New hire {hire.name} ({hire.department}) submitted via intake form, "
               f"start {hire.start_label}.",
    ))
    db.add(models.AuditEvent(
        actor="Orchestrator", is_agent=True, action="Tasks fanned out",
        detail=f"Access tasks created for {hire.name} and routed to owners.",
    ))
    db.commit()
    db.refresh(hire)
    return schemas.HireOut(
        id=hire.id, name=hire.name, department=hire.department,
        start_label=hire.start_label, readiness=0, tasks=[],
    )
