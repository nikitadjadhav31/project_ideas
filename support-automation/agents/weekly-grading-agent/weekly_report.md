# Weekly Support Quality Report
_Generated 2026-09-12T06:08:33.960742+00:00 · sample 10 of 12 closed tickets_

**Mean score:** 71.2%  |  **Pass rate:** 60.0%  |  **Auto-fail rate:** 20.0%

## Summary of recurring patterns
Graded a sample of 10 closed tickets. Mean quality score **71.2%**, clean-pass rate **60%** (>=80%, no auto-fail, no flagged failure), **2** auto-fail(s).

**Auto-fails this week (compliance-critical, score 0%):**
- `C-2002` (dev) — unverified money claim.
- `C-2005` (dev) — missed mandatory escalation.

**Recurring failure patterns:**
- **vague-timeline** — 1 of 10 tickets (10%). 'Shortly'/'ASAP' instead of a specific time.
- **unverified-refund** — 1 of 10 tickets (10%). Refund/credit figures stated without verifying policy.
- **missed-escalation** — 1 of 10 tickets (10%). Emergencies answered instead of escalated.

**Agents to coach (below sample mean or with auto-fails):**
- **dev**: mean 33.0% over 4 ticket(s), 2 auto-fail(s) — most common issue: vague-timeline.

**Weakest category:** `outage` tickets averaged 0.0%, below the 71.2% sample mean.

**Recommended focus for next week:**
1. Zero-tolerance refresh on the auto-fail rules (money verification + mandatory escalation) — these are the highest-cost failures.
2. Target the top recurring pattern (**vague-timeline**) in the next team standup with the specific examples above.

## Per-ticket grades
| Ticket | Agent | Category | Score | Auto-fail | Top tags |
|---|---|---|---|---|---|
| C-2011 | dev | bug | 80% | — | vague-timeline |
| C-2002 | dev | billing | 0% | unverified money claim | unverified-refund |
| C-2001 | priya | billing | 86% | — | — |
| C-2005 | dev | outage | 0% | missed mandatory escalation | missed-escalation |
| C-2004 | dev | bug | 52% | — | incomplete-resolution, templated-tone, no-next-step |
| C-2012 | priya | account | 100% | — | — |
| C-2007 | sam | account | 98% | — | — |
| C-2010 | sam | how_to | 98% | — | — |
| C-2009 | priya | billing | 98% | — | — |
| C-2003 | priya | bug | 100% | — | — |

## Failure-tag frequencies
- vague-timeline: 1
- unverified-refund: 1
- missed-escalation: 1
- incomplete-resolution: 1
- templated-tone: 1
- no-next-step: 1

_Grades produced by applying the ticket-quality-grading skill to each sampled ticket. Money figures are never asserted; auto-fails follow the skill's gates._