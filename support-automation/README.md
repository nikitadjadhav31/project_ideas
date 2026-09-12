# Support Automation — Skills, Agents & the reasoning behind each

Leadership wants an AI assistant to take over five manual support functions. The task was to
decide, for each, whether it needs a **Skill**, an **Agent**, or **Neither** — justify it —
and then build the ones I chose so each works correctly on its own (no orchestration, no
end-to-end pipeline).

**Start with [`docs/DECISIONS.md`](docs/DECISIONS.md)** — it's the core of the submission: the
definitions I classified on, and the reasoning for every one of the five functions (including
the compound ones that split across all three buckets).

## See the agents running

**▶ Interactive console: https://claude.ai/code/artifact/fc139340-d938-4786-862c-93cbbddc2421**

A one-page UI over all three agents, built from their real output:
- **Ticket Triage** — the full routed run, plus a **live classifier**: type any ticket and see
  the deterministic gate + reasoner decide in your browser (logic ported verbatim from
  `triage_agent.py`, gate and all).
- **At-Risk Briefing** — toggle Acme Corp (HIGH risk) vs Globex LLC (LOW) to compare retention
  briefs, churn signals, and call talking points.
- **Weekly Grading** — score distribution, auto-fail rate, per-agent/per-category means, and the
  failure-tag patterns.

The console *displays* real output for all three and *re-runs* the triage logic live; the
briefing and grading agents run offline via the Python below. Source: [`docs/ui/console.html`](docs/ui/console.html).

## The verdicts

| # | Function | Verdict |
|---|----------|---------|
| 1 | Categorize + route tickets; escalate outage/legal/security | **Agent** (+ a deterministic escalation gate — "Neither" — inside it) |
| 2 | Tone + policy-safe outbound replies | **Skill** |
| 3 | At-risk retention briefing from 3 systems | **Agent** |
| 4 | Weekly quality grading of a ticket sample | **Skill** (the rubric) + Agent (weekly runner) + Neither (sampling) |
| 5 | Bug → known-issue check → engineering write-up | **Skill** |

The one-line intuition: **Skills are libraries, Agents are workers, Neither is plumbing.**
Agents call Skills; that relationship drives several of the splits.

## Repository layout

```
support-automation/
├── README.md                     ← you are here
├── docs/
│   ├── DECISIONS.md              ← Skill/Agent/Neither classification + justification (core)
│   ├── AI_USAGE.md               ← what was human-decided vs. AI-generated
│   └── ui/console.html           ← interactive console over all three agents (link above)
├── skills/
│   ├── policy-safe-reply/        ← #2  SKILL.md + references/
│   ├── bug-triage-writeup/       ← #5  SKILL.md + references/
│   ├── ticket-quality-grading/   ← #4  SKILL.md + references/  (the reusable rubric)
│   └── _eval/                    ← adversarial cases + programmatic grader (18/18 pass)
└── agents/
    ├── ticket-triage-agent/      ← #1  agent + deterministic gate + tests + Claude drop-in
    ├── at-risk-briefing-agent/   ← #3  agent + 3 mock systems + tests + Claude drop-in
    └── weekly-grading-agent/     ← #4  agent (reuses the grading skill) + tests + Claude drop-in
```

## What's built

### Skills (invoked capabilities — no autonomy)
- **`skills/policy-safe-reply/`** (#2) — drafts/reviews replies in the company voice and
  never states a refund/price not verified against the live policy doc. Hardcodes the *rule*,
  never a number, so it can't go stale. Includes worked before/after examples.
- **`skills/bug-triage-writeup/`** (#5) — checks the changelog for a known issue, else turns a
  messy report into an engineering-ready write-up (title / env / numbered repro / expected vs.
  actual / severity + priority). Includes a full worked run.
- **`skills/ticket-quality-grading/`** (#4, the reusable unit) — grades one closed ticket on a
  weighted 5-category rubric with auto-fail compliance gates, and emits a scored, evidence-
  backed evaluation with reusable failure tags for pattern-tracking.

### Agents (autonomous loops — runnable now, offline)
- **`agents/ticket-triage-agent/`** (#1) — reads an inbox, escalates on a **deterministic gate
  first** (outage/security/legal, must fire 100%), then uses a swappable reasoner for the
  normal category/team/urgency judgement. Safety only ratchets *up*, never down.
- **`agents/at-risk-briefing-agent/`** (#3) — pulls from three mock systems (billing, usage,
  tickets), computes churn signals deterministically, and synthesizes a one-page retention
  brief with call talking points.
- **`agents/weekly-grading-agent/`** (#4) — on a weekly cadence, deterministically samples
  closed tickets, applies the **grading skill** to each (mock↔Claude swappable), then
  synthesizes a cross-ticket report: score distribution, auto-fail rate, recurring failure-tag
  patterns, per-agent/per-category clustering, and coaching recommendations. This is the agent
  that reuses the ticket-quality-grading skill — the clearest Skill-inside-Agent example.

All three agents use a **pluggable reasoner/synthesizer/grader**: a deterministic mock runs
offline here so you can see real output with no API key, and a `*_claude.py` drop-in implements
the identical interface for production. The agent logic (loop, safety gate, multi-system gather,
risk math, sampling + synthesis) is the same either way.

## Tests

Everything is verified and runs offline:
- **Agents** — unit tests each: `test_triage.py`, `test_briefing.py`, `test_weekly_grading.py`
  (all pass; includes an adversarial test proving the triage safety gate holds even when the
  reasoner misclassifies every ticket).
- **Skills** — a graded eval harness (`skills/_eval/`) applies each skill to fresh adversarial
  cases; **18/18 objective assertions pass**, with judgement-only checks flagged for human
  review rather than faked.

## Run it

All agents run offline with no dependencies and no API key. Run each from the repo root:

```bash
# Ticket triage & routing (#1)
python3 agents/ticket-triage-agent/triage_agent.py
python3 agents/ticket-triage-agent/test_triage.py

# At-risk retention briefing (#3)  — try globex-llc for the healthy-account contrast
python3 agents/at-risk-briefing-agent/briefing_agent.py acme-corp
python3 agents/at-risk-briefing-agent/test_briefing.py

# Weekly quality-grading runner (#4)
python3 agents/weekly-grading-agent/weekly_grading_agent.py
python3 agents/weekly-grading-agent/test_weekly_grading.py

# Skill evaluations — each skill applied to fresh adversarial cases, graded objectively
python3 skills/_eval/grade_evals.py     # 18/18 auto-checkable assertions pass
```

Skills are Markdown: to "run" one, read its `SKILL.md` and apply it to a ticket. Each ships a
`references/` file with a full worked example.

To switch an agent to a live model: `pip install anthropic`, set `ANTHROPIC_API_KEY`, and pass
`ClaudeReasoner()` / `ClaudeSynthesizer()` / `ClaudeGrader()` into the agent constructor.
Nothing else changes.

## AI usage disclosure
See [`docs/AI_USAGE.md`](docs/AI_USAGE.md) for where AI was used, what was researched vs.
generated, and everything I manually changed after generation.
