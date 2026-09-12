# bug-triage-writeup — eval outputs

Produced by following SKILL.md: extract facts → check changelog → branch known/new → set
severity+priority → self-check.

---

## bug-1-known-issue
**Input:** Known-issues: [#4412 "Low contrast on Settings labels in dark mode, fix next
release"]. Customer: "In dark mode the text on the Settings page is basically unreadable, grey
on grey."

**Changelog check:** behavior (dark mode + Settings + contrast/unreadable) matches #4412 →
known issue. Do not open a new ticket.

**Output:**
```
Status: KNOWN ISSUE — no new ticket needed
Matched entry: #4412 Low contrast on Settings labels in dark mode
Customer-reported behavior: Settings text is grey-on-grey / unreadable in dark mode
Current status / ETA: Fix scheduled for next release; no exact date published
Suggested customer reply: You're right, and this one's already on our list — low contrast on
the Settings labels in dark mode is a known issue with a fix landing in our next release. In
the meantime, switching to light mode under Preferences restores full contrast. I'll add your
report to the ticket so we can let you know when it ships.
```

**Self-check:** flagged known + cited #4412 ✓ · no invented date beyond "next release" ✓ ·
honest customer reply with workaround ✓.

---

## bug-2-new-vague
**Input:** Known-issues: [#4412 dark mode contrast, #4501 invite emails delayed]. Customer:
"i try to save my profile changes and it just doesnt save. nothing happens when i hit save.
chrome. really need this fixed"

**Changelog check:** profile-save doing nothing on Save does not match #4412 (dark mode) or
#4501 (invite email latency) → new issue.

**Extraction:** what broke = saving profile changes; trigger = clicking Save on the profile
page; expected = changes persist / confirmation (inferred — not stated); actual = nothing
happens, no confirmation, no error; env = Chrome (version unknown), OS unknown; frequency =
not stated (ask); evidence = none.

**Output:**
```
Title: [Profile] Save on profile edits does nothing (no confirmation, no error) in Chrome

Severity: High
Priority: High

Environment:
- Browser/App version: Chrome (version Unknown — needs follow-up)
- OS / Device: Unknown — needs follow-up
- Plan/Tier: Unknown — needs follow-up

Summary:
Saving profile changes appears to do nothing: clicking Save yields no confirmation and no
error, and the customer reports the changes don't persist. Blocking a routine account action.
Observed behavior only; root cause unconfirmed.

Steps to reproduce:
1. Logged in (role/plan unknown — to confirm), open Profile / account settings.
2. Edit one or more profile fields.
3. Click "Save".

Expected result:
Changes are saved and a confirmation is shown. (inferred)

Actual result:
Nothing happens on Save — no confirmation, no error surfaced, changes reportedly not persisted.

Evidence:
None provided; requested a screen recording + browser console output.

Possibly related:
None (checked #4412 dark mode, #4501 invite latency — neither matches).

Open questions for customer / eng:
- Exact Chrome version + OS?
- Any errors in the browser console when Save is clicked?
- Does it fail every time or intermittently?
- Do the changes fail silently but actually persist after refresh, or truly not save?
```

**Self-check:** checked changelog first ✓ · new write-up (not a false match) ✓ · numbered repro
from a known state ✓ · expected (inferred) + actual both present ✓ · unknowns marked, not
invented ✓ · no asserted root cause ✓ · severity AND priority set ✓.
