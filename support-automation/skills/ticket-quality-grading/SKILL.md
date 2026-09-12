---
name: ticket-quality-grading
description: Use this skill to grade a resolved/closed customer support interaction (email, chat, or ticket thread) against a consistent quality rubric and produce a scored, evidence-backed evaluation. Trigger it whenever someone wants to QA, score, review, or assess the quality of a support reply or ticket — a single ticket or one ticket at a time within a larger sample. It covers the weighted category scores, the auto-fail compliance checks, and the written justification. Use it any time the request is "grade this ticket", "how good was this response", "QA this conversation", or "score this against our rubric".
---

# Ticket Quality Grading

Grade one closed support interaction against a fixed rubric, the same way every time, and
return a score with evidence. Consistency is the whole value here: two different reviewers (or
the same reviewer on two different days) should land on close to the same score for the same
ticket. That only happens if the rubric levels are concrete and every score is tied to a quote
from the ticket rather than a gut feeling.

This skill grades **one interaction**. Grading a weekly sample = running this skill over each
ticket, then summarizing patterns across the results (that cross-ticket summary is a separate
step and not part of this skill).

## Rubric at a glance

Five weighted categories, each scored 1–5, plus three auto-fail compliance gates. The design
follows the standard weighted-scorecard-with-auto-fails model used in support QA: weight the
categories by what matters, and make compliance-critical failures override the score entirely.

| Category | Weight | What it measures |
|---|---|---|
| Resolution | 35% | Was the customer's actual problem solved, correctly and completely? |
| Compliance & accuracy | 25% | Correct info; policy/money claims verified; required steps followed |
| Communication & tone | 25% | Clear, empathetic, on-brand, blame-free |
| Efficiency | 10% | Resolved without unnecessary back-and-forth or delay |
| Proactivity | 5% | Anticipated the next question / prevented the next ticket |

**Weighted score** = Σ(category score ÷ 5 × weight), expressed as 0–100%.

### Auto-fail gates (override everything)

If any of these occurred, the interaction scores **0% overall** regardless of category scores,
and the failure is named explicitly. These are the non-negotiables — the same money/escalation
rules the reply side is held to:

1. **Unverified money claim** — stated a refund, credit, discount, or price that wasn't (or
   couldn't have been) verified against current policy.
2. **Missed mandatory escalation** — an outage, security, or legal trigger was present and the
   agent tried to answer/resolve instead of escalating.
3. **Gave materially wrong/harmful information** — instructions that could cause data loss,
   security exposure, or a clearly incorrect factual claim presented as true.

An auto-fail is still reported with the category scores filled in (so the coaching signal
survives), but the headline result is 0% and the gate that tripped is stated first.

## Scoring anchors

Score each category 1–5 using these anchors. When a ticket falls between two, pick the lower
and say why.

**Resolution (35%)**
- 5 — Problem fully solved, correctly, in a way the customer can act on immediately.
- 3 — Partially solved, or solved but the customer had to do extra work to get there.
- 1 — Not solved, wrong solution, or customer left without a path forward.

**Compliance & accuracy (25%)**
- 5 — All info correct; any money/policy claim verified and sourced; required steps followed.
- 3 — Minor inaccuracy or an unsourced-but-correct claim; no material harm.
- 1 — Incorrect info or unfollowed required step (note: verified-false money/escalation issues
  are auto-fails, not a 1).

**Communication & tone (25%)**
- 5 — Clear, empathetic, on-brand, blame-free; acknowledged emotion before the answer.
- 3 — Understandable but flat, slightly robotic/templated, or thin on empathy where it was
  needed.
- 1 — Confusing, dismissive, blaming, or jargon-heavy; would frustrate the customer.

**Efficiency (10%)**
- 5 — Resolved in the fewest reasonable exchanges; no needless delay or repetition.
- 3 — Some avoidable back-and-forth or a slow-but-not-egregious path.
- 1 — Excessive round-trips, long unexplained gaps, or made the customer repeat themselves.

**Proactivity (5%)**
- 5 — Anticipated the likely next question or prevented a follow-up ticket.
- 3 — Handled what was asked, nothing more.
- 1 — Left obvious loose ends that will generate another ticket.

## Workflow

1. Read the full interaction (all messages, both sides).
2. **Run the auto-fail gates first.** If any trips, note it — you'll still score categories for
   coaching, but the overall result is 0%.
3. Score each of the five categories 1–5 against the anchors. For each, cite specific evidence
   (a short quote or a clear reference to what the agent did or didn't do).
4. Compute the weighted score.
5. Write the justification and the single highest-leverage coaching note.

## Output format

ALWAYS use this exact structure:

```
Ticket: [id / short descriptor]

AUTO-FAIL CHECK: PASS  |  FAIL — [which gate + one-line evidence]

Category scores:
- Resolution (35%):            [1–5] — [evidence]
- Compliance & accuracy (25%): [1–5] — [evidence]
- Communication & tone (25%):  [1–5] — [evidence]
- Efficiency (10%):            [1–5] — [evidence]
- Proactivity (5%):            [1–5] — [evidence]

Weighted score: [NN]%   (0% if AUTO-FAIL)

What went well: [1–2 sentences]
Primary coaching note: [the single most valuable thing to change next time]
Failure tags: [short reusable tags for pattern-tracking, e.g. "no-empathy",
"unverified-refund", "missed-escalation", "incomplete-resolution", "templated-tone"]
```

The **failure tags** matter: they're deliberately short and reusable so that when many graded
tickets are later summarized, recurring patterns can be counted (e.g., "7/20 tickets tagged
templated-tone this week"). Use consistent tag spellings.

## Notes on fair grading

- Grade what the agent could control. Don't penalize them for a product limitation or a policy
  they correctly and kindly conveyed.
- One quote beats a paragraph of opinion. If you can't point to evidence in the ticket, you're
  probably projecting — re-read before scoring.
- A polite, on-brand reply that didn't solve the problem is still a low Resolution score.
  Friendliness doesn't substitute for the fix.

## Example

See `references/example.md` for a fully graded ticket and an auto-fail example.
