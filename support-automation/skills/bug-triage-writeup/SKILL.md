---
name: bug-triage-writeup
description: Use this skill whenever a customer reports something broken or misbehaving and you need to (1) check whether it's already a known issue in the changelog / known-issues list, and (2) if it's new, turn the report into an engineering-ready bug write-up with reproduction steps. Trigger it for any inbound bug, defect, error, crash, "X isn't working", "Y gives the wrong result", or unexpected-behavior report, even when the customer message is vague — the skill covers extracting missing details and deciding known-vs-new. Do NOT use it for how-to questions, feature requests, or billing issues.
---

# Bug Triage & Write-up

Turn a customer's bug report into one of two outcomes, reliably:
1. **Known issue** → confirm the match and point to the existing entry (so engineering isn't
   handed a duplicate).
2. **New issue** → produce a clean, engineering-ready write-up that a developer can act on
   *without coming back to ask questions*. That last part is the whole point: a report that
   forces a round-trip of clarifying questions is a slow report.

## Workflow

1. **Extract the facts** from the customer message (see "What to extract"). Note what's
   missing — you'll either infer it safely or flag it as unknown. Never invent details.
2. **Check the changelog / known-issues list** for a match (see "Known-issue matching"). This
   is a *judgement*, not a string search — the same bug is often described in different words.
3. **Branch:**
   - **Match found** → write the "known issue" output.
   - **No match** → write the full "engineering write-up".
4. **Set severity and priority** using the definitions below — don't eyeball it.
5. **Self-check** against the checklist before handing off.

## What to extract

Pull these from the customer's message. If something isn't stated, mark it `Unknown — needs
follow-up` rather than guessing:

- **What broke** — the specific feature/action, not "the app".
- **Trigger** — what they did right before it broke.
- **Expected vs. actual** — what should have happened vs. what did. If the customer only gives
  one side, infer the expected behavior from the product's normal operation and label it as
  inferred.
- **Environment** — browser + version, OS, device, app/build version, plan/tier if relevant.
  Environment-specific bugs are common, so missing environment is worth a follow-up.
- **Frequency / reproducibility** — every time, or intermittent (e.g., "3 of 5 tries")?
  Intermittent bugs are still valid; say so explicitly.
- **Evidence** — screenshots, error text, request IDs, timestamps. Capture verbatim error
  strings; they're often the fastest path to the root cause.

## Known-issue matching

Compare the extracted bug against the changelog / known-issues list by **behavior**, not
wording. Two reports describe the same bug when the *broken behavior + trigger + affected
area* line up, even if the customer's phrasing, exact numbers, or UI labels differ.

- **Confident match** → known-issue output, link the entry, give status/ETA if the entry has
  one.
- **Partial / uncertain match** → treat as new, but note the possibly-related entry so
  engineering can dedupe. Say why you're unsure (e.g., "similar symptom, different browser").
- **No match** → new issue.

Never force a match to avoid writing it up; a missed-but-real new bug is worse than a dedupe.

## Severity vs. priority

These are different axes. Set both.

**Severity** (how bad the impact is):
- **Critical** — data loss, security exposure, or the product is unusable for the affected
  user/flow with no workaround.
- **High** — a core feature is broken or gives wrong results; a workaround may exist but it's
  painful.
- **Medium** — a non-core feature is broken, or a core feature is degraded with an easy
  workaround.
- **Low** — cosmetic, minor, or edge-case with negligible impact.

**Priority** (how soon to fix) — factors in severity **plus** reach and business context:
number of users affected, whether it's a high-value account, whether it's growing, whether
there's a workaround. A Low-severity bug hitting every user on signup can still be high
priority; a Critical-severity bug on a deprecated feature one customer uses may not be.

Use `Urgent / High / Medium / Low` for priority. If you're unsure of reach, say so and default
priority to match severity.

## Output — known issue

```
Status: KNOWN ISSUE — no new ticket needed
Matched entry: [changelog/known-issues ID or title] ([link if available])
Customer-reported behavior: [one line]
Current status / ETA: [from the entry, or "no ETA published"]
Suggested customer reply: [one or two sentences the agent can adapt — honest about status,
no invented fix date]
```

## Output — engineering write-up

Use this exact template. Keep it complete but tight — every line should save the developer a
question. Title format is `[Area] what breaks (trigger condition)`.

```
Title: [Area] concise description of what breaks (trigger condition)

Severity: Critical | High | Medium | Low
Priority: Urgent | High | Medium | Low

Environment:
- Browser/App version:
- OS / Device:
- Plan/Tier (if relevant):
- (mark any field "Unknown — needs follow-up" if not provided)

Summary:
[2–3 sentences: what's broken, who's affected, why it matters. Observed behavior only — do
not assert a root cause you haven't confirmed.]

Steps to reproduce:
1. [Start from a known state, e.g. "Logged in as an Admin on the Pro plan"]
2. [Exact action — name the actual button/field/value, not "do the thing"]
3. ...
(If intermittent: note frequency, e.g. "Occurs ~3 of 5 attempts.")

Expected result:
[What should happen. If inferred rather than stated by the customer, label it "(inferred)".]

Actual result:
[What actually happens, as observed. Include verbatim error text / codes / request IDs.]

Evidence:
[Screenshots, logs, timestamps, request IDs — or "none provided; requested from customer".]

Possibly related:
[Link any uncertain known-issue match here, or "none".]

Open questions for customer / eng:
[Anything marked Unknown above that would speed up the fix.]
```

## Self-check before handing off

- [ ] Did I actually check the changelog/known-issues before writing a new report?
- [ ] For a new bug: are the repro steps numbered, exact, and startable from a known state?
- [ ] Expected AND actual both present (expected labeled "(inferred)" if I supplied it)?
- [ ] Environment captured, or explicitly marked unknown?
- [ ] Verbatim error text preserved (not paraphrased)?
- [ ] Severity and priority both set, using the definitions — not vibes?
- [ ] Did I avoid asserting a root cause I can't confirm?
- [ ] Nothing invented — every unknown is labeled, not filled in?

## Example

See `references/example.md` for a full run from a messy customer message to a finished
engineering write-up, plus a known-issue example.
