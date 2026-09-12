#!/usr/bin/env python3
"""
Weekly Quality-Grading Runner Agent
===================================

Decision (see docs/DECISIONS.md #4): this function splits three ways, and this agent is the
"Agent" third of it. The other two thirds are honored explicitly in the code structure:

  - SAMPLING  = "Neither" (plumbing): a deterministic rolling random sample of closed tickets.
                See RollingSampler — no LLM, seedable, repeatable.
  - GRADING   = "Skill": applying the fixed quality rubric to ONE ticket, the same way every
                time. See GradingSkill — a faithful executor of
                skills/ticket-quality-grading/SKILL.md (same weights, same auto-fail gates,
                same failure tags). Swappable mock <-> live Claude, like the other agents.
  - WEEKLY RUN = "Agent" (this file's job): on a cadence, autonomously sample -> map the
                grading skill over the sample -> aggregate -> synthesize the cross-ticket
                failure-pattern summary that no single grade can produce.

The cross-ticket synthesis is the reason this is an agent and not just "run the skill N times":
counting recurring failure tags, spotting which agents/categories cluster, and writing the
weekly narrative is analysis over the whole sample.

Agent loop:
    perceive (it's the weekly cadence; a pool of closed tickets exists)
      -> sample      (deterministic rolling random sample)
      -> grade each  (map the grading skill over the sample)
      -> aggregate   (score distribution, auto-fail rate, failure-tag frequencies, clusters)
      -> synthesize  (weekly written summary of recurring patterns + recommendations)
      -> deliver     (markdown report + machine-readable JSON)

Runnable offline: ships a MockGrader so `python weekly_grading_agent.py` produces a real
report with no API key. A live Claude grader implements the same GradingSkill.grade()
interface; see grader_claude.py.
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


HERE = Path(__file__).parent

# Rubric constants — mirrored EXACTLY from skills/ticket-quality-grading/SKILL.md.
WEIGHTS = {
    "resolution": 0.35,
    "compliance": 0.25,
    "communication": 0.25,
    "efficiency": 0.10,
    "proactivity": 0.05,
}
AUTO_FAIL_GATES = ("unverified_money_claim", "missed_mandatory_escalation", "harmful_info")


# --------------------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------------------

@dataclass
class ClosedTicket:
    id: str
    closed_at: str
    category: str
    assigned_agent: str
    customer_message: str
    agent_reply: str


@dataclass
class Grade:
    ticket_id: str
    assigned_agent: str
    category: str
    auto_fail: Optional[str]            # gate name if tripped, else None
    scores: dict                        # category -> 1..5
    weighted_score: int                 # 0..100 (0 if auto_fail)
    failure_tags: list[str]
    coaching_note: str

    @property
    def passed(self) -> bool:
        # A clean pass requires a high score, no auto-fail, AND no flagged failure pattern.
        # A reply that scrapes 80% but still carries a failure tag is not a QA "pass".
        return self.auto_fail is None and self.weighted_score >= 80 and not self.failure_tags


# --------------------------------------------------------------------------------------
# SAMPLING  —  the "Neither" piece: deterministic rolling random sample
# --------------------------------------------------------------------------------------

class RollingSampler:
    """Pick a rolling random sample of closed tickets. Deterministic under a seed so a run is
    reproducible/auditable. No LLM — this is plain plumbing, exactly as classified."""

    def __init__(self, sample_size: int = 10, seed: Optional[int] = None):
        self.sample_size = sample_size
        self.seed = seed

    def sample(self, tickets: list[ClosedTicket]) -> list[ClosedTicket]:
        rng = random.Random(self.seed)
        if len(tickets) <= self.sample_size:
            return list(tickets)
        return rng.sample(tickets, self.sample_size)


# --------------------------------------------------------------------------------------
# GRADING  —  the "Skill" piece: apply the rubric to ONE ticket. Swappable.
# --------------------------------------------------------------------------------------

class GradingSkill:
    """Contract: grade(ticket) -> Grade, applying the ticket-quality-grading rubric. A live
    implementation calls Claude with the SKILL.md rubric; the mock below approximates it so the
    agent runs offline. The agent code never depends on which one is used."""

    def grade(self, ticket: ClosedTicket) -> Grade:  # pragma: no cover - interface
        raise NotImplementedError


class MockGrader(GradingSkill):
    """Heuristic stand-in for the grading skill. NOT the production judgement layer (that's the
    Claude grader) — but it faithfully implements the rubric's *structure*: it runs the three
    auto-fail gates first, scores the five categories, applies the exact weights, and emits the
    same failure tags the skill defines. This lets the weekly agent's real logic (sampling,
    aggregation, synthesis) be exercised end-to-end."""

    # Auto-fail gate 1: money figure asserted in a reply (proxy for "unverified").
    MONEY = re.compile(r"\$\s?\d[\d,]*\s*(refund|back|credit|discount)|\b\d+%\s*(refund|discount|off)\b", re.I)
    # Auto-fail gate 2: an escalation trigger in the customer msg that the reply tried to answer.
    ESCALATION_TRIGGER = re.compile(
        r"\b(outage|down|can'?t log ?in|breach|hacked|unauthor|lawsuit|attorney|gdpr)\b", re.I)
    ESCALATION_HANDLED = re.compile(r"\bescalat", re.I)
    # Auto-fail gate 3: obviously harmful instruction (proxy).
    HARMFUL = re.compile(r"\b(delete your account|drop the database|disable your backups|"
                         r"share your password)\b", re.I)

    BANNED_PHRASES = ["calm down", "as i already told you", "that's not our policy",
                      "nothing we can do", "there's nothing we can do", "you probably"]
    VAGUE_TIME = re.compile(r"\b(shortly|asap|as soon as possible)\b", re.I)
    CONCRETE_TIME = re.compile(r"\b(\d{1,2}\s?(am|pm)|\d{1,2}:\d{2}|within \d+\s?(min|hour)|"
                               r"by (eod|end of day|\d)|tomorrow)\b", re.I)

    def grade(self, t: ClosedTicket) -> Grade:
        msg, reply = t.customer_message.lower(), t.agent_reply.lower()
        tags: list[str] = []

        # ---- Auto-fail gates FIRST (per the skill) ----
        auto_fail = None
        if self.MONEY.search(t.agent_reply):
            auto_fail = "unverified_money_claim"; tags.append("unverified-refund")
        elif self.ESCALATION_TRIGGER.search(msg) and not self.ESCALATION_HANDLED.search(reply):
            auto_fail = "missed_mandatory_escalation"; tags.append("missed-escalation")
        elif self.HARMFUL.search(reply):
            auto_fail = "harmful_info"; tags.append("harmful-advice")

        # ---- Category scores (1..5) ----
        scores = {}

        # Resolution: did the reply actually do something toward a fix?
        solved_signals = ["here's how", "steps", "1.", "workaround", "i've fixed", "i fixed",
                          "try", "go to", "settings", "reset", "i've escalated", "escalated"]
        empty_signals = ["appreciate your patience", "value you as a customer",
                         "have a wonderful day", "have a great day", "sorry to hear"]
        has_solution = any(s in reply for s in solved_signals)
        mostly_empty = (any(s in reply for s in empty_signals) and not has_solution)
        scores["resolution"] = 5 if has_solution else (1 if mostly_empty else 3)
        if scores["resolution"] <= 2:
            tags.append("incomplete-resolution")

        # Compliance & accuracy.
        if auto_fail in ("unverified_money_claim", "harmful_info"):
            scores["compliance"] = 1
        elif auto_fail == "missed_mandatory_escalation":
            scores["compliance"] = 1
        else:
            scores["compliance"] = 5

        # Communication & tone.
        banned_hit = [p for p in self.BANNED_PHRASES if p in reply]
        if banned_hit:
            scores["communication"] = 1; tags.append("dismissive-tone")
        elif mostly_empty:
            scores["communication"] = 3; tags.append("templated-tone")
        else:
            scores["communication"] = 5

        # Efficiency: concrete next step/time vs. vague or a non-answer.
        if mostly_empty:
            scores["efficiency"] = 2; tags.append("no-next-step")
        elif self.VAGUE_TIME.search(reply) and not self.CONCRETE_TIME.search(reply):
            scores["efficiency"] = 3; tags.append("vague-timeline")
        else:
            scores["efficiency"] = 5

        # Proactivity: anticipated the next question?
        proactive = any(s in reply for s in ["in the meantime", "also", "you might also",
                                             "to prevent", "next time", "i'll follow up",
                                             "i'll update you"])
        scores["proactivity"] = 5 if proactive else (1 if mostly_empty else 3)

        # ---- Weighted score ----
        weighted = round(sum((scores[c] / 5) * w for c, w in WEIGHTS.items()) * 100)
        if auto_fail:
            weighted = 0

        coaching = self._coach(auto_fail, scores, tags)
        # de-dup tags, keep order
        seen = set(); tags = [x for x in tags if not (x in seen or seen.add(x))]
        return Grade(
            ticket_id=t.id, assigned_agent=t.assigned_agent, category=t.category,
            auto_fail=auto_fail, scores=scores, weighted_score=weighted,
            failure_tags=tags, coaching_note=coaching,
        )

    @staticmethod
    def _coach(auto_fail, scores, tags) -> str:
        if auto_fail == "unverified_money_claim":
            return ("Never state a refund/credit figure before verifying against the charge and "
                    "current policy; acknowledge and follow up with the exact amount.")
        if auto_fail == "missed_mandatory_escalation":
            return ("An outage/security/legal trigger was present — escalate immediately instead "
                    "of trying to resolve in the reply.")
        if auto_fail == "harmful_info":
            return "Reply contained a potentially harmful instruction; review before sending."
        lowest = min(scores, key=scores.get)
        return {
            "resolution": "Tone is not a substitute for a fix — address the actual problem or "
                          "ask the one question needed to.",
            "communication": "Watch the tone: avoid dismissive/templated phrasing; lead with "
                             "empathy then the answer.",
            "efficiency": "Give a concrete next step and a specific time, not 'shortly'.",
            "proactivity": "Anticipate the likely follow-up to prevent a second ticket.",
            "compliance": "Double-check accuracy and that required steps were followed.",
        }[lowest]


# --------------------------------------------------------------------------------------
# WEEKLY RUN  —  the "Agent": sample -> grade -> aggregate -> synthesize
# --------------------------------------------------------------------------------------

@dataclass
class WeeklyReport:
    generated_at: str
    sample_size: int
    pool_size: int
    pass_rate: float
    auto_fail_rate: float
    mean_score: float
    grades: list[Grade]
    tag_frequencies: dict
    per_agent: dict
    per_category: dict
    narrative: str


class WeeklyGradingAgent:
    def __init__(self, grader: GradingSkill | None = None,
                 sampler: RollingSampler | None = None):
        self.grader = grader or MockGrader()
        self.sampler = sampler or RollingSampler(sample_size=10, seed=42)

    def run(self, pool: list[ClosedTicket]) -> WeeklyReport:
        print(f"[weekly-grading] pool of {len(pool)} closed tickets")
        sample = self.sampler.sample(pool)
        print(f"  [sample]  drew {len(sample)} tickets (seed={self.sampler.seed})")

        grades = [self.grader.grade(t) for t in sample]
        print(f"  [grade]   applied rubric to {len(grades)} tickets")

        # ---- aggregation (cross-ticket; this is the agent's real work) ----
        n = len(grades)
        auto_fails = [g for g in grades if g.auto_fail]
        passes = [g for g in grades if g.passed]
        mean_score = round(sum(g.weighted_score for g in grades) / n, 1) if n else 0.0

        tag_freq = Counter(tag for g in grades for tag in g.failure_tags)

        per_agent = defaultdict(lambda: {"n": 0, "mean": 0.0, "auto_fails": 0, "tags": Counter()})
        per_cat = defaultdict(lambda: {"n": 0, "mean": 0.0, "auto_fails": 0})
        for g in grades:
            a = per_agent[g.assigned_agent]
            a["n"] += 1; a["mean"] += g.weighted_score
            a["auto_fails"] += 1 if g.auto_fail else 0
            a["tags"].update(g.failure_tags)
            c = per_cat[g.category]
            c["n"] += 1; c["mean"] += g.weighted_score
            c["auto_fails"] += 1 if g.auto_fail else 0
        for d in per_agent.values():
            d["mean"] = round(d["mean"] / d["n"], 1)
            d["tags"] = dict(d["tags"])
        for d in per_cat.values():
            d["mean"] = round(d["mean"] / d["n"], 1)

        print(f"  [aggregate] mean={mean_score}%  auto-fails={len(auto_fails)}  "
              f"pass={len(passes)}/{n}")

        narrative = self._synthesize(grades, tag_freq, per_agent, per_cat,
                                     mean_score, auto_fails, passes)

        return WeeklyReport(
            generated_at=datetime.now(timezone.utc).isoformat(),
            sample_size=n, pool_size=len(pool),
            pass_rate=round(len(passes) / n * 100, 1) if n else 0.0,
            auto_fail_rate=round(len(auto_fails) / n * 100, 1) if n else 0.0,
            mean_score=mean_score, grades=grades,
            tag_frequencies=dict(tag_freq.most_common()),
            per_agent=dict(per_agent), per_category=dict(per_cat),
            narrative=narrative,
        )

    def _synthesize(self, grades, tag_freq, per_agent, per_cat, mean, auto_fails, passes) -> str:
        """The cross-ticket written summary of recurring failure patterns. This is what a single
        grade cannot give you and why the weekly run is an agent."""
        n = len(grades)
        L = []
        L.append(f"Graded a sample of {n} closed tickets. Mean quality score **{mean}%**, "
                 f"clean-pass rate **{round(len(passes)/n*100)}%** (>=80%, no auto-fail, no "
                 f"flagged failure), **{len(auto_fails)}** auto-fail(s).")
        L.append("")

        if auto_fails:
            L.append("**Auto-fails this week (compliance-critical, score 0%):**")
            for g in auto_fails:
                L.append(f"- `{g.ticket_id}` ({g.assigned_agent}) — "
                         f"{g.auto_fail.replace('_',' ')}.")
            L.append("")

        if tag_freq:
            top = tag_freq.most_common(3)
            L.append("**Recurring failure patterns:**")
            for tag, count in top:
                share = round(count / n * 100)
                L.append(f"- **{tag}** — {count} of {n} tickets ({share}%). "
                         f"{self._tag_gloss(tag)}")
            L.append("")

        # Agent cluster: who is furthest below the mean, if anyone.
        weak = [(a, d) for a, d in per_agent.items() if d["mean"] < mean - 10 or d["auto_fails"]]
        if weak:
            L.append("**Agents to coach (below sample mean or with auto-fails):**")
            for a, d in sorted(weak, key=lambda x: x[1]["mean"]):
                worst = Counter(d["tags"]).most_common(1)
                worst_tag = f" — most common issue: {worst[0][0]}" if worst else ""
                L.append(f"- **{a}**: mean {d['mean']}% over {d['n']} ticket(s), "
                         f"{d['auto_fails']} auto-fail(s){worst_tag}.")
            L.append("")

        # Category cluster.
        worst_cat = min(per_cat.items(), key=lambda x: x[1]["mean"]) if per_cat else None
        if worst_cat and worst_cat[1]["mean"] < mean:
            L.append(f"**Weakest category:** `{worst_cat[0]}` tickets averaged "
                     f"{worst_cat[1]['mean']}%, below the {mean}% sample mean.")
            L.append("")

        # Recommendation.
        L.append("**Recommended focus for next week:**")
        if auto_fails:
            L.append("1. Zero-tolerance refresh on the auto-fail rules (money verification + "
                     "mandatory escalation) — these are the highest-cost failures.")
        if tag_freq:
            L.append(f"{'2' if auto_fails else '1'}. Target the top recurring pattern "
                     f"(**{tag_freq.most_common(1)[0][0]}**) in the next team standup with the "
                     f"specific examples above.")
        if not auto_fails and not tag_freq:
            L.append("1. No systemic issues in this sample — maintain and spot-check next week.")
        return "\n".join(L)

    @staticmethod
    def _tag_gloss(tag: str) -> str:
        return {
            "unverified-refund": "Refund/credit figures stated without verifying policy.",
            "missed-escalation": "Emergencies answered instead of escalated.",
            "incomplete-resolution": "Replies that didn't actually solve the problem.",
            "templated-tone": "Warm-but-hollow replies with no substance.",
            "dismissive-tone": "Blaming or dismissive language.",
            "no-next-step": "No concrete next action for the customer.",
            "vague-timeline": "'Shortly'/'ASAP' instead of a specific time.",
            "harmful-advice": "Potentially damaging instructions.",
        }.get(tag, "")


# --------------------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------------------

def render_markdown(r: WeeklyReport) -> str:
    L = []
    L.append(f"# Weekly Support Quality Report")
    L.append(f"_Generated {r.generated_at} · sample {r.sample_size} of {r.pool_size} closed "
             f"tickets_")
    L.append("")
    L.append(f"**Mean score:** {r.mean_score}%  |  **Pass rate:** {r.pass_rate}%  |  "
             f"**Auto-fail rate:** {r.auto_fail_rate}%")
    L.append("")
    L.append("## Summary of recurring patterns")
    L.append(r.narrative)
    L.append("")
    L.append("## Per-ticket grades")
    L.append("| Ticket | Agent | Category | Score | Auto-fail | Top tags |")
    L.append("|---|---|---|---|---|---|")
    for g in r.grades:
        af = g.auto_fail.replace("_", " ") if g.auto_fail else "—"
        tags = ", ".join(g.failure_tags) if g.failure_tags else "—"
        L.append(f"| {g.ticket_id} | {g.assigned_agent} | {g.category} | "
                 f"{g.weighted_score}% | {af} | {tags} |")
    L.append("")
    L.append("## Failure-tag frequencies")
    if r.tag_frequencies:
        for tag, c in r.tag_frequencies.items():
            L.append(f"- {tag}: {c}")
    else:
        L.append("- none")
    L.append("")
    L.append("_Grades produced by applying the ticket-quality-grading skill to each sampled "
             "ticket. Money figures are never asserted; auto-fails follow the skill's gates._")
    return "\n".join(L)


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------

def load_pool(path: Path) -> list[ClosedTicket]:
    return [ClosedTicket(**t) for t in json.loads(path.read_text())]


def main(argv: list[str]) -> int:
    pool_path = Path(argv[1]) if len(argv) > 1 else HERE / "mock_closed_tickets.json"
    pool = load_pool(pool_path)

    agent = WeeklyGradingAgent()
    report = agent.run(pool)

    md = render_markdown(report)
    (HERE / "weekly_report.md").write_text(md)
    (HERE / "weekly_report.json").write_text(
        json.dumps({**asdict(report),
                    "grades": [asdict(g) for g in report.grades]}, indent=2))
    print("\n" + "=" * 78)
    print(md)
    print("=" * 78)
    print(f"\nWrote weekly_report.md and weekly_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
