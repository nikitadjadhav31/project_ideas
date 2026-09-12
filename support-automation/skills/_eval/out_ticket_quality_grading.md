# ticket-quality-grading — eval outputs

Produced by following SKILL.md: read interaction → run auto-fail gates FIRST → score 5
categories against anchors with evidence → compute weighted score → justification + tags.

---

## grade-1-autofail
**Input:** Customer: "Was I overcharged?" Agent: "Yes! I've confirmed a $150 refund, back in
3-5 days. Cheers!"

**Auto-fail gate:** the agent asserted a specific "$150 refund" — a money figure — with no
sign it was verified against the charge record or current policy. Gate 1 (unverified money
claim) trips.

```
Ticket: grade-1 — overcharge refund

AUTO-FAIL CHECK: FAIL — Unverified money claim: stated a specific "$150 refund" with no
evidence the amount or eligibility was verified against billing records / current policy.

Category scores (recorded for coaching):
- Resolution (35%):            2 — Promised a resolution, but on an unverified figure, so it may
                                   be wrong; not a safe resolution.
- Compliance & accuracy (25%): 1 — Core violation: refund amount asserted from nowhere.
- Communication & tone (25%):  3 — Friendly, but the breezy "Cheers!" underplays a billing error.
- Efficiency (10%):            5 — Single reply.
- Proactivity (5%):            1 — Didn't confirm the charge before committing money.

Weighted score: 0%   (AUTO-FAIL)

What went well: Fast, upbeat acknowledgement.
Primary coaching note: Never state a refund amount before verifying the charge and the policy.
Safe move: acknowledge, say you're confirming the details, follow up with the exact figure.
Failure tags: unverified-refund, premature-promise
```

**Self-check vs. assertions:** auto-fail triggered ✓ · overall 0% ✓ · categories still scored
for coaching ✓ · reusable tag `unverified-refund` present ✓.

---

## grade-2-polite-unresolved
**Input:** Customer: "My export is missing half the rows." Agent: "So sorry to hear that! Our
team really appreciates your patience and we value you as a customer. Have a wonderful day!"

**Auto-fail gate:** no money claim, no missed mandatory escalation, no harmful/wrong info →
PASS. This is a quality problem, not a compliance breach.

```
Ticket: grade-2 — export missing rows

AUTO-FAIL CHECK: PASS

Category scores:
- Resolution (35%):            1 — The actual problem (missing rows) was not addressed at all;
                                   no fix, no workaround, no next step, no questions asked.
- Compliance & accuracy (25%): 4 — Nothing incorrect stated; but nothing verified/actioned either.
- Communication & tone (25%):  3 — Warm words, but empty reassurance where the customer needed a
                                   fix; reads as a templated brush-off.
- Efficiency (10%):            2 — 'Closed' in one message, but the customer must now come back —
                                   negative real efficiency.
- Proactivity (5%):            1 — Left the entire issue open; a guaranteed follow-up ticket.

Weighted score: 47%

What went well: Polite, non-defensive, positive tone.
Primary coaching note: Tone is not a substitute for solving the problem. Acknowledge, then
either reproduce/triage the export issue or ask the one question needed to (row count, filters,
file). A friendly non-answer still fails the customer.
Failure tags: incomplete-resolution, templated-tone, no-next-step
```

**Self-check vs. assertions:** Resolution low (1) because nothing solved ✓ · NOT an auto-fail —
a real but nonzero 47% ✓ · warm tone noted but did not inflate Resolution ✓.
