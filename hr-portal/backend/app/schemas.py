"""Pydantic request/response models (the API contract shared with the SPA)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tool: str
    scope: str
    approver_name: str | None
    approver_email: str | None
    status: str
    nudge_count: int
    escalated: bool
    sensitive: bool
    requires_manual: bool
    step: str | None
    last_nudge: str          # computed label, e.g. "3 nudges, escalated"
    waiting_label: str       # computed label, e.g. "Waiting 2 days"


class HireOut(BaseModel):
    id: int
    name: str
    department: str
    start_label: str
    readiness: int           # 0-100, share of tasks provisioned
    tasks: list[TaskOut]


class Stats(BaseModel):
    active_hires: int
    awaiting_approval: int
    escalated: int


class DashboardOut(BaseModel):
    stats: Stats
    hires: list[HireOut]


class ApprovalItem(BaseModel):
    id: int
    tool: str
    scope: str
    hire_name: str
    waiting_label: str
    sensitive: bool
    requires_manual: bool
    step: str | None


class ApproverRequest(BaseModel):
    approver_name: str
    approver_email: str
    initials: str
    items: list[ApprovalItem]


class ReplyIn(BaseModel):
    approver_email: str
    text: str


class ReplyResultItem(BaseModel):
    tool: str
    scope: str
    hire_name: str
    outcome: str             # "approved" | "rejected" | "not_authorised"
    note: str


class ReplyResult(BaseModel):
    intent: str              # "Approve" | "Reject" | "Unclear"
    applied_count: int
    skipped_count: int
    items: list[ReplyResultItem]


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    timestamp: datetime
    actor: str
    is_agent: bool
    action: str
    detail: str
    refused: bool


class HireCreate(BaseModel):
    name: str
    department: str
    start_label: str
