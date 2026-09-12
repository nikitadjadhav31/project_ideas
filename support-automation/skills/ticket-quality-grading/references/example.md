# Worked grading examples

## Example A — normal ticket, scored

**Interaction:**
> **Customer:** "My invoices are showing the wrong company name. How do I fix it?"
> **Agent:** "Happy to help! You can update that under Settings → Billing → Company details —
> just edit the 'Legal name' field and hit Save, and it'll apply to all future invoices. Past
> invoices keep the old name for audit reasons, but if you need a corrected copy of a specific
> one, tell me the invoice number and I'll regenerate it for you. Anything else I can sort out?"

**Grading:**

```
Ticket: #8821 — invoice company name

AUTO-FAIL CHECK: PASS

Category scores:
- Resolution (35%):            5 — Gave exact path (Settings → Billing → Company details) and
                                   handled the edge case (past invoices) with an offer to fix.
- Compliance & accuracy (25%): 5 — Correct steps; the audit-trail explanation is accurate; no
                                   money figure asserted.
- Communication & tone (25%):  5 — Warm, clear, contractions, offered a next step; on-brand.
- Efficiency (10%):            5 — Fully resolved in a single reply, no back-and-forth needed.
- Proactivity (5%):            5 — Pre-empted the "but what about old invoices" follow-up and
                                   offered regeneration unprompted.

Weighted score: 100%

What went well: Complete one-touch resolution that anticipated the follow-up question.
Primary coaching note: Nothing significant — model example of proactive resolution.
Failure tags: none
```

---

## Example B — auto-fail (unverified money claim)

**Interaction:**
> **Customer:** "I was double-charged this month, can I get a refund?"
> **Agent:** "So sorry about that! Yes, I've gone ahead and confirmed you'll get a full $79
> refund, it'll be back in 3–5 days. Have a great day!"

**Grading:**

```
Ticket: #8822 — double charge refund

AUTO-FAIL CHECK: FAIL — Unverified money claim: asserted a specific "$79 refund" without any
sign the amount or eligibility was verified against current policy/billing records.

Category scores (recorded for coaching):
- Resolution (35%):            3 — May have resolved it, but the promised amount is unverified,
                                   so the "resolution" could be wrong.
- Compliance & accuracy (25%): 1 — Stated a specific refund figure from memory; core policy
                                   violation.
- Communication & tone (25%):  4 — Warm and empathetic, good acknowledgement of the error.
- Efficiency (10%):            5 — Single reply.
- Proactivity (5%):            2 — Didn't confirm the charge details before promising money.

Weighted score: 0%   (AUTO-FAIL)

What went well: Empathetic, fast acknowledgement of the customer's frustration.
Primary coaching note: Never state a refund amount before verifying the charge and the policy.
The safe move: acknowledge, say you're confirming the details, and follow up with the exact
amount.
Failure tags: unverified-refund, premature-promise
```
