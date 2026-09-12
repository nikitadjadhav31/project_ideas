"""
Live Claude grader — drop-in replacement for MockGrader.

Usage in production:
    from grader_claude import ClaudeGrader
    agent = WeeklyGradingAgent(grader=ClaudeGrader())

This makes the "Skill" third of the function a real skill invocation: it sends each ticket to
Claude with the ticket-quality-grading rubric and parses back a structured Grade. The agent's
sampling and cross-ticket synthesis are unchanged — only the per-ticket judgement is upgraded
from heuristic to model. Requires `pip install anthropic` and ANTHROPIC_API_KEY. Left
un-imported by default so the agent runs offline with the mock.

The system prompt below is a compressed form of skills/ticket-quality-grading/SKILL.md. In a
real deployment you would load that SKILL.md file directly rather than duplicate it here.
"""

from __future__ import annotations

import json
import os

from weekly_grading_agent import GradingSkill, ClosedTicket, Grade, WEIGHTS

_SYSTEM = """You grade one closed customer-support interaction against a fixed quality rubric.

Run the AUTO-FAIL gates FIRST. If any occurred, overall score is 0 but still fill category
scores for coaching. Gates:
- unverified_money_claim: stated a refund/credit/discount/price not verified against policy.
- missed_mandatory_escalation: an outage/security/legal trigger was present and the reply tried
  to resolve instead of escalating.
- harmful_info: instructions that could cause data loss/security exposure or a clearly wrong
  claim presented as true.

Score each category 1-5 (5 best):
- resolution (weight 35%): was the actual problem solved with a usable path forward?
- compliance (25%): correct info; policy/money claims verified; required steps followed.
- communication (25%): clear, empathetic, on-brand, blame-free.
- efficiency (10%): resolved without needless back-and-forth; concrete next step/time.
- proactivity (5%): anticipated the next question / prevented a follow-up ticket.

Weighted score = sum(category/5 * weight) * 100, rounded; 0 if any auto-fail.

Use short reusable failure_tags from this set where they apply: unverified-refund,
missed-escalation, incomplete-resolution, templated-tone, dismissive-tone, no-next-step,
vague-timeline, harmful-advice.

Respond with ONLY this JSON, no prose:
{"auto_fail": null | "unverified_money_claim" | "missed_mandatory_escalation" | "harmful_info",
 "scores": {"resolution": n, "compliance": n, "communication": n, "efficiency": n, "proactivity": n},
 "failure_tags": [...],
 "coaching_note": "one sentence"}
"""


class ClaudeGrader(GradingSkill):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model

    def grade(self, t: ClosedTicket) -> Grade:
        msg = self._client.messages.create(
            model=self._model, max_tokens=400, system=_SYSTEM,
            messages=[{"role": "user", "content":
                       f"Customer: {t.customer_message}\n\nAgent reply: {t.agent_reply}"}],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        d = json.loads(text)

        scores = {c: int(d["scores"].get(c, 3)) for c in WEIGHTS}
        auto_fail = d.get("auto_fail")
        weighted = 0 if auto_fail else round(
            sum((scores[c] / 5) * w for c, w in WEIGHTS.items()) * 100)
        return Grade(
            ticket_id=t.id, assigned_agent=t.assigned_agent, category=t.category,
            auto_fail=auto_fail, scores=scores, weighted_score=weighted,
            failure_tags=list(d.get("failure_tags", [])),
            coaching_note=d.get("coaching_note", ""),
        )
