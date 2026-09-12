# Worked examples

## Example A — messy report → engineering write-up (new issue)

**Customer message:**
> "hey so im trying to invite my teammate and it just spins forever and nothing happens. tried
> like 4 times. im on chrome. this is really annoying we need her in today"

**Changelog check:** searched known issues for invite / team-member / seat behavior. Nearest
entry is "Invite emails delayed up to 10 min (2026-08)" — that's about *delivery latency*, not
the invite action hanging. Behavior doesn't line up → treat as new, note as possibly related.

**Extraction:**
- What broke: sending a team invite
- Trigger: clicking Send on the invite dialog
- Expected: invite is created / email sent (inferred — customer didn't state it)
- Actual: button spins indefinitely, no confirmation, no error
- Environment: Chrome (version unknown), OS unknown, plan unknown
- Frequency: 4 of 4 attempts → consistent
- Evidence: none provided

**Write-up:**

```
Title: [Team invites] Invite dialog hangs indefinitely on Send (no error, no confirmation)

Severity: High
Priority: High

Environment:
- Browser/App version: Chrome (version Unknown — needs follow-up)
- OS / Device: Unknown — needs follow-up
- Plan/Tier: Unknown — needs follow-up

Summary:
Sending a team invite hangs: the Send button enters a loading state and never resolves — no
success confirmation and no error surfaced. Reproduced by the customer 4 of 4 times, blocking
them from adding a teammate they need today. Observed behavior only; root cause unconfirmed.

Steps to reproduce:
1. Logged in (plan/role unknown — to confirm), open the Team / Members page.
2. Click "Invite member".
3. Enter a teammate's email address.
4. Click "Send".

Expected result:
Invite is created and a confirmation is shown / invite email is queued. (inferred)

Actual result:
Send button shows a loading spinner indefinitely; no confirmation, no error message, invite
does not appear to be created. Occurs 4 of 4 attempts.

Evidence:
None provided; requested screenshot + browser console output from customer.

Possibly related:
"Invite emails delayed up to 10 min (2026-08)" — likely unrelated (that's delivery latency,
this is the action hanging), flagged for dedupe only.

Open questions for customer / eng:
- Exact Chrome version + OS?
- Any errors in the browser console when Send is clicked?
- Plan/tier and whether the account is at its seat limit (could a full-seat state hang instead
  of erroring?).
```

Note how "at seat limit?" is raised as an open question, not asserted as the cause — the skill
forbids claiming an unconfirmed root cause.

---

## Example B — known issue (no new ticket)

**Customer message:**
> "Dark mode makes the Settings text unreadable, it's grey on grey."

**Changelog check:** known-issues list contains "Low contrast on Settings labels in dark mode
(#4412), fix in next release." Behavior matches (dark mode + Settings + contrast).

**Output:**

```
Status: KNOWN ISSUE — no new ticket needed
Matched entry: #4412 Low contrast on Settings labels in dark mode
Customer-reported behavior: Settings text is grey-on-grey / unreadable in dark mode
Current status / ETA: Fix scheduled for next release; no exact date published
Suggested customer reply: You're right, and this one's already on our list — low contrast on
the Settings labels in dark mode is a known issue with a fix coming in our next release. In the
meantime, switching to light mode under Preferences restores full contrast. I'll note your
report on the ticket so we can let you know when it ships.
```
