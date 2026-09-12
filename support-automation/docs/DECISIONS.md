# Skill vs. Agent vs. Neither — Classification & Rationale

## Working definitions (the axis I'm classifying on)

**Skill** — A reusable, invoked capability: a `SKILL.md` (plus optional scripts/reference
files) that encodes *how to do one thing correctly and consistently*. It has no autonomy.
Something or someone calls it. Its value is **consistency and correctness of a procedure or
judgement**, not initiative. Good fit when the task is: bounded, repeatable, judgement-heavy
but not decision-branching across tools, and the same "recipe" applies every time.

**Agent** — An autonomous loop: perceive → decide → act (call tools) → observe → repeat,
usually triggered by an *event* or a *schedule* rather than a person asking each time. Its
value is **initiative and orchestration across systems/state**. Good fit when the task
requires: reacting to things as they arrive, pulling from multiple live systems, branching
decisions, or running unattended on a cadence.

**Neither** — Deterministic plumbing where an LLM adds cost and failure modes without adding
judgement. A keyword match, a scheduled query, a webhook, a DB join. Best served by ordinary
software; an LLM in the path is a liability (non-determinism on a task that must be exact).

A useful test: *Skills are libraries; Agents are workers; Neither is plumbing.* An Agent
frequently **uses** Skills. That relationship is the crux of several decisions below.

---

## 1. Read, categorize, and route new tickets; immediately escalate outage / legal / security

**Verdict: AGENT — but with one carved-out "Neither" sub-piece.**

Routing new tickets is the textbook agent case: it is **event-triggered** (a ticket arrives),
it must **act unattended within minutes**, and it **branches** — categorize, then either queue
to a team or fire an escalation. No human invokes it per ticket; that's the whole point of
handing it over.

The carve-out: the phrase *"anything touching a live outage or a legal/security keyword needs
immediate escalation."* A hard keyword/severity match that must fire **100% of the time** is
exactly what an LLM should **not** be the sole gatekeeper of — non-determinism on a
must-never-miss safety path is a bug, not a feature. The right design is **deterministic
pre-filter (Neither) → agent for the nuanced 95%.** So the escalation *trigger* is Neither
(a regex/rule that runs before the model and can also run as a backstop after it), while the
*categorize-and-route* judgement is the Agent. I build the agent to run the deterministic
check first and treat the LLM as second opinion, never as the only line of defense.

Why not a Skill: a skill can't watch the inbox or decide on its own to escalate. It would just
sit there until called.

---

## 2. Every outbound reply matches tone-of-voice and never states an out-of-policy refund/price

**Verdict: SKILL.**

This is a *how-to-write-it-correctly* problem, invoked whenever a reply is being drafted
(by a human agent, or by a triage/response agent). It is the same recipe every time: apply the
voice, and **never assert a refund/pricing number that isn't in the current policy doc.**
That's consistency-of-output, which is what skills are for.

The interesting constraint is "never state a figure not in the *frequently-updated* policy doc."
That pushes toward a skill that does **not hardcode numbers** — it hardcodes the *rule*
("look it up in the live doc; if you can't verify it, don't state it; here's the safe
deflection language") and a verification checklist. Baking today's refund amounts into the
skill would rot immediately.

Why not an Agent: nothing here is autonomous or multi-system. It's a quality/guardrail layer
on a single artifact (the reply). Wrapping it in an agent adds no initiative, only overhead.

Why not Neither: tone-matching and "is this claim policy-safe?" are genuine language
judgements. A regex can catch a `$` sign but can't tell whether a stated figure matches
policy or whether the voice is right.

---

## 3. Assemble a one-page retention briefing for an "at-risk" customer from 3 systems

**Verdict: AGENT.**

This needs to **pull from three separate live systems** (billing, product-usage logs, past
tickets), reconcile them, and **synthesize** a decision-support document. Multi-system
retrieval + synthesis toward a goal is agent work. It's on-demand rather than scheduled
("before a retention call"), but on-demand doesn't make it a skill — the defining trait is the
autonomous gathering and cross-referencing across tools, not who pressed go.

There's a real skill *hiding inside* it — "what a good one-page retention brief looks like" is
a reusable format/judgement. In a bigger build I'd factor that out as a briefing-format skill
the agent consumes. For this task I keep the briefing format as a template the agent owns, and
note the factoring explicitly, to avoid over-engineering a second artifact nobody asked for.

Why not a Skill alone: a skill can't reach into billing/usage/tickets and fetch state. It can
only tell you how to format what's already in front of you.

---

## 4. Weekly graded sample of closed tickets against a rubric + written failure-pattern summary

**Verdict: split — the RUBRIC is a SKILL; the WEEKLY RUN is an AGENT; the SAMPLING is Neither.**

This one is deliberately compound and the cleanest illustration of the three-way split:

- **"Grade one ticket against the quality rubric"** is a **Skill** — a fixed rubric applied
  consistently, the same way every time. This is the reusable judgement unit, and it's also
  the same rubric the reply-writing side should be measured against, so it earns independent
  existence.
- **"Every week, pull a sample, grade them all, write up the recurring failure patterns"** is
  an **Agent** — scheduled, unattended, iterates over N tickets (invoking the grading skill on
  each), then does cross-ticket synthesis a single grade can't produce.
- **"Pull a rolling random sample of closed tickets"** is **Neither** — a scheduled query with
  a random sample. Deterministic; no LLM needed to `SELECT ... ORDER BY random() LIMIT n`.

I build the **grading rubric as a Skill** (the reusable, independently valuable unit). The
weekly orchestration and sampling I document as agent/plumbing but do **not** build, because
the task says build what I decide is a skill or an agent and *not* wire up pipelines — the
grading skill is the piece that stands on its own and is reused elsewhere. (See "What I am
deliberately not building.")

---

## 5. Bug report: check the changelog for a known issue; if new, write it up for engineering with repro steps

**Verdict: SKILL.**

This is a defined procedure with a fixed output contract: check-known-issue, and if new,
produce an engineering-ready write-up (title, environment, steps to reproduce, expected vs.
actual, severity). Same recipe every time → skill. It's the kind of thing invoked *mid-flow*
by whoever/whatever is handling the ticket.

The one wrinkle: "check whether it's a known issue in the changelog" implies a lookup. If that
changelog is a searchable system, the *search* is a tool the skill tells you to use; the skill
supplies the **matching judgement** ("is this the same issue?" is fuzzy — versions, wording,
partial repros) and the **write-up format**. That judgement is why it's not Neither: string
-matching a changelog misses "same bug, described differently."

Why not an Agent: there's no loop and no autonomy — it's a single well-defined transformation
from "customer bug report" to "engineering ticket," invoked on demand. It reads as a skill the
triage agent (piece 1) would call when it classifies a ticket as a bug.

---

## Summary table

| # | Function | Verdict | Core reason |
|---|----------|---------|-------------|
| 1 | Categorize + route tickets | **Agent** (+ Neither for the hard escalation trigger) | Event-driven, unattended, branches across teams |
| 2 | Tone + policy-safe replies | **Skill** | Invoked per-reply; consistency guardrail; no autonomy |
| 3 | At-risk retention briefing | **Agent** | Multi-system retrieval + synthesis |
| 4 | Weekly quality grading | **Skill** (rubric) + Agent (weekly run) + Neither (sampling) | Rubric is reusable judgement; the cadence is the agent |
| 5 | Bug → engineering write-up | **Skill** | Fixed procedure + output contract, invoked on demand |

## What I am building
- **Skill:** Policy-safe reply guide (#2)
- **Skill:** Bug triage & engineering write-up (#5)
- **Skill:** Ticket-quality grading rubric (#4, the reusable unit)
- **Agent:** Ticket triage & routing, deterministic-escalation-first (#1)
- **Agent:** At-risk retention briefing (#3)
- **Agent:** Weekly quality-grading runner (#4) — added after the initial build. It is the
  cleanest illustration of the three-way split in code: it wires the **rolling sampler**
  ("Neither" — deterministic, seedable), maps the **grading skill** ("Skill" — one ticket at a
  time, mock↔Claude swappable) over the sample, and does the **cross-ticket synthesis** that
  makes the weekly run an Agent (recurring-pattern summary, per-agent/per-category clustering,
  recommendations). It reuses the grading rubric rather than duplicating it, so it does not
  violate the "don't duplicate the skill" concern noted below.

## What I am deliberately NOT building (and why)
- **No orchestration / pipeline** — explicitly out of scope per the task. Note: the weekly
  grading runner is a *single* agent with a clear I/O contract (pool in → report out), not a
  pipeline wiring multiple components together, so it stays within scope. What remains
  un-built is any cross-component wiring (e.g. the triage agent calling the bug or reply
  skills), and the scheduler/cron that would invoke the weekly runner on a cadence — that
  trigger is infrastructure, not agent logic.
- **The deterministic escalation regex as a separate deliverable** — it lives *inside* the
  triage agent as its first-pass gate (and is shown there), rather than as a standalone artifact,
  because on its own it's plumbing, not a skill or an agent.
