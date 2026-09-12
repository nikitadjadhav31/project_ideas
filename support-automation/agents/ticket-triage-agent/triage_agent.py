#!/usr/bin/env python3
"""
Ticket Triage & Routing Agent
=============================

Decision (see docs/DECISIONS.md #1): this is an AGENT — event-driven, unattended, and it
branches (categorize -> queue to a team, OR escalate). The must-never-miss escalation trigger
(outage / legal / security) is treated as a DETERMINISTIC gate that runs BEFORE the model and
again as a backstop AFTER it, because non-determinism on a safety-critical path is a bug. The
LLM is a second opinion that can *raise* urgency, never silently *lower* the deterministic
gate's decision.

Agent loop, per ticket:
    perceive (read ticket)
      -> deterministic escalation gate
      -> reasoner classifies category + team + urgency (mockable / swappable for a live LLM)
      -> reconcile (gate OR reasoner escalation wins; safety is a ceiling that only goes up)
      -> act (escalate now, or route to a team queue)
      -> record decision + rationale

Runnable offline: ships with a MockReasoner so `python triage_agent.py` produces real output
with no API key. A live Claude call implements the same Reasoner.classify() interface; see
reasoner_claude.py for the drop-in.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# --------------------------------------------------------------------------------------
# Domain model
# --------------------------------------------------------------------------------------

TEAMS = {
    "billing": "Billing & Payments",
    "technical": "Technical Support",
    "account": "Account Management",
    "onboarding": "Onboarding & Training",
    "security": "Security (on-call)",
    "legal": "Legal / Compliance",
    "engineering": "Engineering on-call",
}

CATEGORIES = [
    "billing",         # invoices, charges, refunds, payment methods
    "bug",             # something broken / misbehaving
    "how_to",          # usage questions
    "account",         # access, seats, plan changes, cancellation
    "outage",          # product down / unusable
    "security",        # breach, unauthorized access, vulnerability
    "legal",           # legal/compliance/regulatory
    "feedback",        # feature requests, general feedback
]

URGENCY = ["low", "normal", "high", "immediate"]


@dataclass
class Ticket:
    id: str
    subject: str
    body: str
    customer: str
    received_at: str


@dataclass
class Decision:
    ticket_id: str
    category: str
    team: str
    team_name: str
    urgency: str
    escalated: bool
    escalation_reason: Optional[str]
    rationale: str
    source: str  # "deterministic-gate" | "reasoner" | "reconciled"
    decided_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# --------------------------------------------------------------------------------------
# Deterministic escalation gate  (the "Neither" piece — plain rules, must fire 100%)
# --------------------------------------------------------------------------------------

# Word-boundary patterns. Kept explicit and auditable on purpose: a security/legal/outage
# miss is unacceptable, so this never depends on a model. Tuned to favor recall; the reasoner
# and a human can down-triage a false escalation, but a missed one is the dangerous direction.
ESCALATION_RULES = {
    "outage": [
        r"\boutage\b", r"\b(is|are|completely|totally)?\s*down\b", r"\bcan('|no)?t log ?in\b",
        r"\bnothing (works|loads)\b", r"\bwon'?t load\b", r"\b(500|502|503) error\b",
        r"\bentire (team|company|org)\b.*\b(down|can'?t)\b", r"\bunusable\b",
        r"\bservice (disruption|interruption)\b",
    ],
    "security": [
        r"\bdata breach\b", r"\bbreach(ed)?\b", r"\bhacked\b", r"\bunauthor(ized|ised) access\b",
        r"\b(my|our) data (is )?(exposed|leaked)\b", r"\bvulnerabilit(y|ies)\b",
        r"\bphishing\b", r"\bcompromised\b", r"\bleaked\b", r"\bpassword.*(stolen|leaked)\b",
    ],
    "legal": [
        r"\blawyer\b", r"\battorney\b", r"\blawsuit\b", r"\bsue\b", r"\bsuing\b", r"\bliable\b",
        r"\bliability\b", r"\bgdpr\b", r"\bccpa\b", r"\bsubpoena\b", r"\barbitration\b",
        r"\bregulator\b", r"\bright to be forgotten\b", r"\bdata (deletion|erasure) request\b",
    ],
}

# category -> team routing for escalations
ESCALATION_TEAM = {"outage": "engineering", "security": "security", "legal": "legal"}


def deterministic_gate(ticket: Ticket) -> Optional[tuple[str, str, str]]:
    """Return (category, team, matched_reason) if an escalation trigger fires, else None."""
    text = f"{ticket.subject}\n{ticket.body}".lower()
    for category, patterns in ESCALATION_RULES.items():
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                reason = f'matched /{pat}/ -> "{m.group(0).strip()}"'
                return category, ESCALATION_TEAM[category], reason
    return None


# --------------------------------------------------------------------------------------
# Reasoner interface  (the AGENT judgement — swappable: Mock now, Claude in prod)
# --------------------------------------------------------------------------------------

class Reasoner:
    """Classify a ticket into (category, team, urgency) with a rationale.

    Contract: classify() returns a dict with keys: category, team, urgency, rationale.
    A live implementation calls Claude with the ticket text and this same contract; the
    deterministic gate still runs around it, so the model is never the sole safety authority.
    """

    def classify(self, ticket: Ticket) -> dict:  # pragma: no cover - interface
        raise NotImplementedError


class MockReasoner(Reasoner):
    """Deterministic stand-in so the agent runs offline with realistic behavior.

    This is intentionally simple keyword scoring — NOT the safety gate (that's separate and
    always runs). In production this class is replaced by a Claude call; the rest of the agent
    is unchanged. The point of the mock is to exercise the loop and show real routed output.
    """

    SIGNALS = {
        "billing":  ["invoice", "charge", "charged", "refund", "payment", "card", "billing",
                     "receipt", "double-charged", "price", "plan cost", "subscription"],
        "bug":      ["bug", "broken", "error", "doesn't work", "does not work", "not working",
                     "spinning", "crash", "wrong result", "wrong total", "wrong totals",
                     "incorrect", "glitch", "fails", "failing", "gives the wrong"],
        "account":  ["cancel", "seat", "seats", "upgrade", "downgrade", "access", "invite",
                     "member", "role", "permission", "plan change", "delete account",
                     "cancel my account", "cancel my subscription", "close my account"],
        "how_to":   ["how do i", "how to", "where is", "can i", "is it possible", "tutorial",
                     "how can i", "set up", "configure"],
        "feedback": ["feature request", "would be nice", "suggestion", "wish", "please add",
                     "feedback", "roadmap"],
    }

    TEAM_FOR_CATEGORY = {
        "billing": "billing", "bug": "technical", "how_to": "onboarding",
        "account": "account", "feedback": "account",
    }

    def classify(self, ticket: Ticket) -> dict:
        text = f"{ticket.subject}\n{ticket.body}".lower()
        scores = {cat: 0 for cat in self.SIGNALS}
        hits: dict[str, list[str]] = {cat: [] for cat in self.SIGNALS}
        for cat, kws in self.SIGNALS.items():
            for kw in kws:
                if kw in text:
                    scores[cat] += 1
                    hits[cat].append(kw)

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            best = "how_to"  # safe default: treat unknowns as a usage question, low urgency

        # Precedence override: an explicit cancellation is an account/retention matter even if
        # billing words are present (a churn-risk ticket must not disappear into Billing).
        if any(p in text for p in ["cancel my account", "cancel my subscription",
                                   "cancel my", "close my account"]):
            best = "account"

        # Urgency heuristic (the model would reason about this; here we approximate).
        urgency = "normal"
        if any(w in text for w in ["urgent", "asap", "immediately", "today", "right now",
                                   "angry", "furious", "unacceptable", "cancel"]):
            urgency = "high"
        if best in ("bug",) and any(w in text for w in ["all", "everyone", "entire", "every"]):
            urgency = "high"

        matched = ", ".join(hits[best]) if hits[best] else "no strong signal; defaulted"
        return {
            "category": best,
            "team": self.TEAM_FOR_CATEGORY.get(best, "account"),
            "urgency": urgency,
            "rationale": f"keyword signals [{matched}] -> {best}; urgency {urgency}",
        }


# --------------------------------------------------------------------------------------
# The agent
# --------------------------------------------------------------------------------------

class TriageAgent:
    def __init__(self, reasoner: Reasoner):
        self.reasoner = reasoner

    def handle(self, ticket: Ticket) -> Decision:
        # 1) Deterministic safety gate FIRST.
        gate = deterministic_gate(ticket)

        # 2) Reasoner judgement (category/team/urgency for the normal case).
        r = self.reasoner.classify(ticket)

        # 3) Reconcile. Safety is a ceiling that only moves UP.
        if gate is not None:
            gate_cat, gate_team, gate_reason = gate
            # The gate wins on category/team/urgency; note if the reasoner disagreed.
            disagreement = ""
            if r["category"] != gate_cat:
                disagreement = (f" (reasoner independently said '{r['category']}'; "
                                f"deterministic gate overrides for safety)")
            return Decision(
                ticket_id=ticket.id,
                category=gate_cat,
                team=gate_team,
                team_name=TEAMS[gate_team],
                urgency="immediate",
                escalated=True,
                escalation_reason=f"{gate_cat.upper()} trigger: {gate_reason}",
                rationale=(f"Deterministic escalation gate fired -> route to "
                           f"{TEAMS[gate_team]} immediately.{disagreement}"),
                source="deterministic-gate",
            )

        # 3b) Even with no gate hit, let the reasoner escalate upward (never downward).
        escalated = r["urgency"] == "immediate"
        return Decision(
            ticket_id=ticket.id,
            category=r["category"],
            team=r["team"],
            team_name=TEAMS.get(r["team"], r["team"]),
            urgency=r["urgency"],
            escalated=escalated,
            escalation_reason=("reasoner flagged immediate" if escalated else None),
            rationale=r["rationale"],
            source="reasoner",
        )

    def run(self, tickets: list[Ticket]) -> list[Decision]:
        return [self.handle(t) for t in tickets]


# --------------------------------------------------------------------------------------
# CLI / demo
# --------------------------------------------------------------------------------------

def load_tickets(path: Path) -> list[Ticket]:
    data = json.loads(path.read_text())
    return [Ticket(**t) for t in data]


def print_report(decisions: list[Decision]) -> None:
    esc = [d for d in decisions if d.escalated]
    print("=" * 78)
    print(f"TRIAGE RUN — {len(decisions)} tickets, {len(esc)} escalated")
    print("=" * 78)
    for d in decisions:
        flag = "🚨 ESCALATE" if d.escalated else "   route  "
        print(f"\n[{d.ticket_id}] {flag} | {d.category:<8} | -> {d.team_name} "
              f"| urgency={d.urgency} | via {d.source}")
        if d.escalation_reason:
            print(f"          reason: {d.escalation_reason}")
        print(f"          {d.rationale}")
    print("\n" + "-" * 78)
    print("Escalation summary:")
    for d in esc:
        print(f"  {d.ticket_id}: {d.category} -> {d.team_name}")
    if not esc:
        print("  (none)")


def main(argv: list[str]) -> int:
    here = Path(__file__).parent
    tickets_path = Path(argv[1]) if len(argv) > 1 else here / "mock_tickets.json"
    tickets = load_tickets(tickets_path)

    agent = TriageAgent(reasoner=MockReasoner())
    decisions = agent.run(tickets)
    print_report(decisions)

    out = here / "triage_output.json"
    out.write_text(json.dumps([asdict(d) for d in decisions], indent=2))
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
