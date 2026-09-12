#!/usr/bin/env python3
"""
At-Risk Customer Retention Briefing Agent
=========================================

Decision (see docs/DECISIONS.md #3): this is an AGENT. Its defining trait is autonomous
retrieval across THREE separate live systems (billing, product-usage logs, past tickets) plus
synthesis into a decision-support artifact. A skill can't reach into three systems and pull
state; it can only format what's already in front of it.

Agent loop:
    perceive (an account is flagged "at risk")
      -> gather: fetch from billing + usage + tickets connectors  (multi-system retrieval)
      -> analyze: compute objective risk signals from the raw data (deterministic)
      -> synthesize: turn signals into a one-page brief with talking points (reasoner-swappable)
      -> deliver: emit the one-page markdown brief

The "analyze" layer is deterministic on purpose: churn signals (usage decline %, late
payments, negative-CSAT bug pattern, downgrades) should be computed the same way every time.
The "synthesize" layer is where a live Claude call would craft the narrative and call talking
points; here a MockSynthesizer produces a solid brief offline so the agent runs with no key.
The reusable "what a good brief looks like" format lives in the synthesizer — in a larger
build it would be factored out as its own skill the agent consumes.

Runnable offline: `python briefing_agent.py acme-corp`
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SYS_DIR = Path(__file__).parent / "mock_systems"


# --------------------------------------------------------------------------------------
# Connectors — one per system. In production each wraps a real API/DB client. The agent
# only depends on the .fetch(account_id) contract, so swapping mock -> live is local.
# --------------------------------------------------------------------------------------

class Connector:
    name = "base"
    _file = ""

    def fetch(self, account_id: str) -> Any:
        data = json.loads((SYS_DIR / self._file).read_text())
        return data.get(account_id)


class BillingConnector(Connector):
    name, _file = "billing", "billing.json"


class UsageConnector(Connector):
    name, _file = "usage", "usage.json"


class TicketsConnector(Connector):
    name, _file = "tickets", "tickets.json"

    def fetch(self, account_id: str) -> Any:
        data = json.loads((SYS_DIR / self._file).read_text())
        return data.get(account_id, [])


# --------------------------------------------------------------------------------------
# Analysis — deterministic churn signals computed from the raw multi-system data.
# --------------------------------------------------------------------------------------

@dataclass
class RiskSignal:
    label: str
    severity: str   # "info" | "watch" | "risk" | "critical"
    detail: str


def pct_change(new: float, old: float) -> float:
    if old == 0:
        return 0.0
    return round((new - old) / old * 100, 1)


def analyze(billing: dict, usage: dict, tickets: list[dict]) -> list[RiskSignal]:
    signals: list[RiskSignal] = []

    # --- Usage decline (the strongest leading churn indicator) ---
    if usage:
        seat_chg = pct_change(usage["active_seats_last_30d"], usage["active_seats_prev_30d"])
        if seat_chg <= -40:
            sev = "critical"
        elif seat_chg <= -20:
            sev = "risk"
        elif seat_chg < 0:
            sev = "watch"
        else:
            sev = "info"
        signals.append(RiskSignal(
            "Active-seat trend",
            sev,
            f"{usage['active_seats_prev_30d']} -> {usage['active_seats_last_30d']} active seats "
            f"in 30d ({seat_chg:+}%).",
        ))

        login_chg = pct_change(usage["logins_last_30d"], usage["logins_prev_30d"])
        if login_chg < -30:
            signals.append(RiskSignal(
                "Login volume", "risk",
                f"Logins fell {login_chg:+}% ({usage['logins_prev_30d']} -> "
                f"{usage['logins_last_30d']}).",
            ))

        # Seat utilization vs. what they pay for.
        if billing:
            util = round(usage["active_seats_last_30d"] / billing["seats_purchased"] * 100)
            sev = "critical" if util < 40 else "risk" if util < 60 else "info"
            tail = ("Paying for unused capacity." if util < 80
                    else "Healthy utilization.")
            signals.append(RiskSignal(
                "Seat utilization", sev,
                f"{usage['active_seats_last_30d']} of {billing['seats_purchased']} "
                f"purchased seats active ({util}%). {tail}",
            ))

        # Un-adopted high-value features = weak stickiness.
        stale = [f for f, s in usage["feature_adoption"].items()
                 if s in ("unused_last_60d", "never_configured")]
        if stale:
            signals.append(RiskSignal(
                "Feature adoption", "risk",
                f"Key features not in use: {', '.join(stale)}. Low product entrenchment.",
            ))

    # --- Billing risk ---
    if billing:
        if billing.get("failed_payments_last_90d", 0) > 0:
            signals.append(RiskSignal(
                "Payment health", "watch",
                f"{billing['failed_payments_last_90d']} failed/late payment(s) in 90d.",
            ))
        if billing.get("downgrade_history"):
            last = billing["downgrade_history"][-1]
            signals.append(RiskSignal(
                "Downgrade history", "risk",
                f"Downgraded on {last['date']}: {last['from']} -> {last['to']}.",
            ))

    # --- Support experience ---
    if tickets:
        neg = [t for t in tickets if t.get("sentiment") == "negative"]
        low_csat = [t for t in tickets if isinstance(t.get("csat"), int) and t["csat"] <= 2]
        # Recurring same-category bug pain is especially corrosive.
        bug_subjects = [t["subject"].lower() for t in tickets if t.get("category") == "bug"]
        recurring = any(
            sum(1 for s in bug_subjects if kw in s) >= 2
            for kw in ("report", "export", "integration")
        )
        # Also honor an explicit repeat signal in the subject or CSM note ("again", "second
        # report", "still"), which is how recurrence usually shows up in real ticket data.
        repeat_words = ("again", "second", "still", "recurring", "same issue", "same bug")
        for t in tickets:
            blob = f"{t.get('subject','')} {t.get('note','')}".lower()
            if t.get("category") == "bug" and any(w in blob for w in repeat_words):
                recurring = True
                break
        if neg:
            signals.append(RiskSignal(
                "Support sentiment", "risk" if len(neg) >= 2 else "watch",
                f"{len(neg)} of {len(tickets)} recent tickets had negative sentiment; "
                f"{len(low_csat)} scored CSAT <= 2.",
            ))
        if recurring:
            signals.append(RiskSignal(
                "Recurring defect", "critical",
                "Same class of bug reported repeatedly (unresolved pain, not one-off).",
            ))

    return signals


def overall_risk(signals: list[RiskSignal]) -> str:
    order = {"info": 0, "watch": 1, "risk": 2, "critical": 3}
    if not signals:
        return "unknown"
    top = max(order[s.severity] for s in signals)
    n_risk = sum(1 for s in signals if order[s.severity] >= 2)
    if top == 3 or n_risk >= 3:
        return "HIGH"
    if top == 2 or n_risk >= 1:
        return "MEDIUM"
    return "LOW"


# --------------------------------------------------------------------------------------
# Synthesis — turn signals into the one-page brief. Swappable for a live Claude call.
# --------------------------------------------------------------------------------------

class Synthesizer:
    def brief(self, ctx: dict) -> str:  # pragma: no cover - interface
        raise NotImplementedError


class MockSynthesizer(Synthesizer):
    """Produces the one-page brief offline. The format here is the reusable 'good brief'
    contract; a live Claude synthesizer would fill the same sections with richer narrative
    and more tailored call talking points."""

    def brief(self, ctx: dict) -> str:
        b, u, ts = ctx["billing"], ctx["usage"], ctx["tickets"]
        signals: list[RiskSignal] = ctx["signals"]
        risk = ctx["risk"]

        def sev_icon(s):
            return {"critical": "🔴", "risk": "🟠", "watch": "🟡", "info": "🟢"}[s]

        # Talking points derived from the strongest signals — the "so what for the call".
        talking = []
        crit_and_risk = [s for s in signals if s.severity in ("critical", "risk")]
        for s in crit_and_risk[:4]:
            if s.label == "Active-seat trend":
                talking.append("Lead with the usage drop — ask what changed internally "
                               "(reorg? project ended? switched tools?). This is the "
                               "conversation, not the pricing.")
            elif s.label == "Recurring defect":
                talking.append("Acknowledge the repeated bug directly and bring an eng "
                               "status/owner to the call. Trust was damaged; don't gloss it.")
            elif s.label == "Feature adoption":
                talking.append("Offer hands-on help configuring the unused high-value "
                               "features — un-adopted features are why churn feels painless.")
            elif s.label == "Seat utilization":
                talking.append("Get ahead of a downgrade ask: propose a right-sized plan or "
                               "a re-onboarding push to re-activate dormant seats.")
            elif s.label == "Downgrade history":
                talking.append("They've already downgraded once — treat this as the second "
                               "step toward leaving unless reversed.")
        if not talking:
            talking.append("No acute risk signals; use the call to deepen the relationship "
                           "and surface expansion opportunities.")

        renewal = b.get("renewal_date", "unknown") if b else "unknown"
        tenure = b.get("customer_since", "unknown") if b else "unknown"

        lines = []
        lines.append(f"# Retention Brief — {b['company_name'] if b else ctx['account_id']}")
        lines.append("")
        lines.append(f"**Overall churn risk: {risk}**  |  Renewal: {renewal}  |  "
                     f"Customer since: {tenure}")
        if b:
            lines.append(f"**Plan:** {b['plan']}  |  **MRR:** ${b['mrr_usd']:,}  |  "
                         f"**Contract value:** ${b['contract_value_usd']:,}  |  "
                         f"**Payment status:** {b['payment_status']}")
        lines.append("")
        lines.append("## Risk signals")
        for s in sorted(signals, key=lambda x: {"critical":0,"risk":1,"watch":2,"info":3}[x.severity]):
            lines.append(f"- {sev_icon(s.severity)} **{s.label}** — {s.detail}")
        lines.append("")
        lines.append("## Support history (recent)")
        if ts:
            for t in ts[:5]:
                csat = t.get("csat", "—")
                lines.append(f"- `{t['date']}` [{t['category']}] {t['subject']} "
                             f"(sentiment: {t.get('sentiment','?')}, CSAT: {csat})")
        else:
            lines.append("- No recent tickets on file.")
        lines.append("")
        lines.append("## Recommended talking points for the call")
        for i, tp in enumerate(talking, 1):
            lines.append(f"{i}. {tp}")
        lines.append("")
        lines.append("## Suggested outcome to aim for")
        if risk == "HIGH":
            lines.append("- Save play: bring an eng fix commitment + a re-onboarding offer. "
                         "Consider a goodwill gesture within policy (verify with Billing — do "
                         "NOT promise a figure on the call).")
        elif risk == "MEDIUM":
            lines.append("- Stabilize: address the top signal, confirm value, and set a "
                         "check-in before renewal.")
        else:
            lines.append("- Grow: healthy account; explore expansion / advocacy.")
        lines.append("")
        lines.append("_Generated by the At-Risk Briefing Agent from billing + usage + "
                     "tickets. Money figures are historical record only; verify any "
                     "offer against current policy before the call._")
        return "\n".join(lines)


# --------------------------------------------------------------------------------------
# The agent
# --------------------------------------------------------------------------------------

class BriefingAgent:
    def __init__(self, synthesizer: Synthesizer | None = None):
        self.connectors = {
            "billing": BillingConnector(),
            "usage": UsageConnector(),
            "tickets": TicketsConnector(),
        }
        self.synthesizer = synthesizer or MockSynthesizer()

    def gather(self, account_id: str) -> dict:
        gathered = {}
        for name, conn in self.connectors.items():
            gathered[name] = conn.fetch(account_id)
            status = "ok" if gathered[name] else "no data"
            print(f"  [gather] {name:<8} … {status}")
        return gathered

    def run(self, account_id: str) -> str:
        print(f"[briefing-agent] flagged at-risk: {account_id}")
        g = self.gather(account_id)
        if not any(g.values()):
            return f"# Retention Brief — {account_id}\n\nNo data found in any system."

        signals = analyze(g["billing"] or {}, g["usage"] or {}, g["tickets"] or [])
        risk = overall_risk(signals)
        print(f"  [analyze] {len(signals)} signals; overall risk = {risk}")

        brief = self.synthesizer.brief({
            "account_id": account_id,
            "billing": g["billing"],
            "usage": g["usage"],
            "tickets": g["tickets"],
            "signals": signals,
            "risk": risk,
        })
        return brief


def main(argv: list[str]) -> int:
    account = argv[1] if len(argv) > 1 else "acme-corp"
    agent = BriefingAgent()
    brief = agent.run(account)

    out = Path(__file__).parent / f"brief_{account}.md"
    out.write_text(brief)
    print("\n" + "=" * 78)
    print(brief)
    print("=" * 78)
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
