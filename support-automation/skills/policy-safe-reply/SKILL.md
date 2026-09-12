---
name: policy-safe-reply
description: Use this skill whenever drafting, rewriting, or reviewing an outbound customer support reply (email, chat, or ticket response) so it matches the company tone of voice and never states a refund amount, discount, credit, or price that isn't verified against the current policy document. Trigger it for any customer-facing reply that touches money, cancellations, refunds, plan pricing, or that needs a tone/quality pass before sending — even if the person only says "reply to this ticket" or "help me respond." Also use it to check a drafted reply for outage/legal/security language that must be escalated instead of answered.
---

# Policy-Safe Reply

Draft and review customer support replies that (1) sound like the company, and (2) never
put an unverified money figure or an unescalated emergency in front of a customer. These two
failure modes — wrong tone and wrong/invented policy claims — are the ones that damage trust
and create liability, so they get the most attention here.

The single rule that overrides everything else: **you may not state a refund amount, credit,
discount, or price unless you have just verified it against the current policy/pricing
document. Policy changes frequently. If you cannot verify it right now, do not state it —
deflect with a commitment to follow up.** This skill deliberately contains **no dollar
figures, percentages, or plan prices**, because any number written here would go stale. The
numbers live in the live doc; this skill only tells you how to handle them.

## Workflow

1. **Read the customer's message fully.** Identify the emotional state (calm, confused,
   frustrated, angry) and the request type (bug, billing/refund, how-to, complaint,
   cancellation, feature request).
2. **Run the escalation check FIRST** (see "Escalate, don't answer" below). If it trips, do
   not write a normal reply — write an acknowledgement-and-escalation reply and stop.
3. **Check for money claims.** If the reply will mention a refund, credit, discount, or price,
   go to "The money rule" and follow it before writing the number.
4. **Draft in the company voice** using the voice guide and the structure template for the
   request type.
5. **Run the pre-send checklist.** Fix anything it catches. Then send / hand back.

## Escalate, don't answer

Some messages must be routed to the right team immediately, not resolved in the reply. If the
customer's message contains any of these, acknowledge urgency and escalate — do **not**
attempt a resolution, a workaround, or a policy answer:

- **Live outage / can't-use-the-product**: "everything is down", "site won't load", "can't log
  in at all", "API returning 500s", "outage", "nothing works".
- **Security**: "data breach", "hacked", "unauthorized access", "my data is exposed",
  "vulnerability", "leaked", "phishing".
- **Legal**: "lawyer", "attorney", "lawsuit", "sue", "liable", "GDPR request", "subpoena",
  "arbitration", "regulator".

Escalation reply pattern (fill in the real team + realistic timeline):

> I understand this is urgent, and I'm treating it that way. I've escalated this to our
> [security / engineering / legal] team right now, and [name/role] will get back to you by
> [concrete time]. I'll stay on this with you until it's resolved.

Do not promise an outcome ("we'll refund you", "we'll fix it tonight"). Promise the
**handoff and the follow-up time** only.

## The money rule

Before writing any refund amount, credit, discount, or price:

1. Open the current policy / pricing document. If you don't have access to it in this moment,
   you cannot state the figure — use the deflection language below.
2. Confirm the customer's specifics (plan/tier, purchase date, usage) that the policy keys off.
3. State the figure **and** cite where it comes from ("under our current refund policy…",
   with a link where possible). Stating the source is what makes the claim checkable and keeps
   the reply honest if policy later changes.

**Banned unless just verified against the live doc:**
"We can refund you $X" · "That plan is $X/month" · "You'll get a X% discount" · "You're
entitled to a credit" · "Everyone on your tier gets…"

**Safe deflection when you can't verify right now:**
> I want to give you an accurate answer on this rather than guess, so I'm checking our current
> policy now. I'll follow up by [concrete time] today with exactly what applies to your
> account.

A slightly delayed correct answer is always better than an instant wrong one about money.

## Company voice

The principle (borrowed from teams like Mailchimp who do this well): **voice stays constant,
tone flexes with the customer's emotional state.** You always sound like the same company; you
sound gentler with someone who's upset and more efficient with someone who just wants a fact.

**Always sound:** warm, clear, confident, human.

- Write like a thoughtful colleague, not a policy manual. Use contractions (we're, I'll, it's).
- Short sentences. Everyday words. One idea per sentence.
- Lead with empathy, then the answer — acknowledge the concern before explaining limits.
- Be direct about what you can and can't do. Owning a limit builds more trust than hedging.
- Sign off as a person, not "The Support Team".
- Give **specific** timelines ("by 5pm ET today"), never "shortly" or "ASAP".

**Never say (these read as dismissive or blaming):**
"Calm down." · "As I already told you." · "That's not our policy." · "You need to…" ·
"There's nothing we can do." · "Per our records…" · "You probably clicked the wrong thing."

**Tone flex by emotion:**
- *Angry / frustrated* → validate first, no jokes, take personal ownership ("I'm looking into
  this myself"), shortest path to a fix.
- *Confused* → slow down, number the steps, define terms, offer to hop on a call.
- *Calm / transactional* → be efficient and friendly; don't over-apologize or pad.

## Reply structures

Use the structure that matches the request type. These are scaffolds, not scripts — always
personalize.

**Bug report:** acknowledge it's not expected behavior → (one clarifying question if needed) →
workaround now, if any → escalation + real ETA if it's a real defect.

**Billing / refund:** thank them → say you're checking their account and the policy → explain
what their specifics mean → state what you can do, citing the policy → concrete next step.
(Obey the money rule throughout.)

**Complaint / escalation:** validate the feeling → take personal ownership → say what went
wrong → fix it or escalate to who can → commit to a follow-up time.

**How-to:** confirm what they're trying to do → numbered steps from a known starting point →
offer the next thing they'll likely need.

## Pre-send checklist

- [ ] **Escalation:** No outage/security/legal trigger left un-escalated?
- [ ] **Money:** Every figure verified against the live doc and its source cited? No banned
      phrase used from memory?
- [ ] **Empathy:** Did I acknowledge the concern before the answer (esp. if they're upset)?
- [ ] **Blame:** Nothing that blames the customer or dismisses them?
- [ ] **Specifics:** Concrete timeline, not "shortly"? Personalized, not a raw template?
- [ ] **Voice:** Contractions, short sentences, signed as a person? Would I feel helped
      reading this?
- [ ] **Promises:** Did I only promise things I can control (handoff, follow-up), not
      outcomes I can't guarantee?

## Worked examples

See `references/examples.md` for full before/after replies covering a refund request where the
figure can't be verified, a bug with a workaround, an angry cancellation threat, and an outage
message that must be escalated rather than answered. Read it when you want a concrete model to
match.
