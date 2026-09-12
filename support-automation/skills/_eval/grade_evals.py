#!/usr/bin/env python3
"""
Skill eval grader.

Checks the produced skill outputs against the objective assertions in eval_cases.json. Some
assertions are checkable with deterministic rules (e.g. "no dollar-figure refund promise"),
which is what a good eval does rather than eyeballing. Assertions that need judgement are
listed and marked for human review.

Run: python3 grade_evals.py
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).parent

OUT_FILES = {
    "policy-safe-reply": "out_policy_safe_reply.md",
    "bug-triage-writeup": "out_bug_triage_writeup.md",
    "ticket-quality-grading": "out_ticket_quality_grading.md",
}

# Deterministic checks keyed by assertion id. Each takes the full output text (lowercased for
# convenience is done inside) and returns (passed: bool|None, evidence: str). None => needs
# human judgement, reported separately.
BANNED_PHRASES = ["calm down", "as i already told you", "that's not our policy",
                  "nothing we can do", "there's nothing we can do"]

MONEY_PROMISE = re.compile(r"\$\s?\d[\d,]*\s*(refund|back|credit|discount)", re.I)
VAGUE_TIME = re.compile(r"\b(shortly|asap|as soon as possible)\b", re.I)
CONCRETE_TIME = re.compile(r"\b(\d{1,2}\s?(am|pm)|\d{1,2}:\d{2}|within \d+\s?(min|minute|hour)"
                           r"|by (eod|end of day|\d))", re.I)


def check(assertion_id: str, text: str):
    t = text.lower()
    if assertion_id == "no_invented_figure":
        m = MONEY_PROMISE.search(text)
        return (m is None, f"money-promise match: {m.group(0)!r}" if m else "no $-figure promise")
    if assertion_id == "commits_to_verify":
        ok = any(w in t for w in ["checking", "i'm pulling", "confirm", "verify", "follow up"])
        return (ok, "mentions checking/verifying + follow-up" if ok else "no verify/deflect language")
    if assertion_id == "concrete_time":
        return (CONCRETE_TIME.search(text) is not None and VAGUE_TIME.search(text) is None,
                "has concrete time, no vague filler")
    if assertion_id == "no_banned_phrase" or assertion_id == "tone_not_rewarded_as_resolution":
        hit = [p for p in BANNED_PHRASES if p in t]
        if assertion_id == "no_banned_phrase":
            return (not hit, f"banned: {hit}" if hit else "no banned phrases")
    if assertion_id == "escalates":
        ok = "escalat" in t
        return (ok, "contains escalation language" if ok else "no escalation")
    if assertion_id == "no_outcome_promise":
        # crude: should not promise a fix time / cause; flag 'fixed by', 'root cause is'
        bad = re.search(r"(fixed by|will be fixed|root cause is|caused by)", t)
        return (bad is None, "no fix-time/cause promise" if not bad else f"promise: {bad.group(0)}")
    if assertion_id == "flags_known":
        ok = "known issue" in t and "#4412" in text
        return (ok, "marked KNOWN ISSUE + cited #4412" if ok else "missing known-issue flag/cite")
    if assertion_id == "writes_new_ticket":
        ok = "title:" in t and "steps to reproduce" in t
        return (ok, "full write-up present" if ok else "no write-up structure")
    if assertion_id == "numbered_repro":
        ok = bool(re.search(r"steps to reproduce:\s*\n\s*1\.", text, re.I))
        return (ok, "numbered repro starting at 1" if ok else "no numbered repro")
    if assertion_id == "expected_and_actual":
        ok = "expected result" in t and "actual result" in t
        return (ok, "expected + actual present" if ok else "missing one")
    if assertion_id == "marks_unknowns":
        ok = "unknown" in t
        return (ok, "unknowns explicitly marked" if ok else "no unknown markers")
    if assertion_id == "sev_and_pri":
        ok = "severity:" in t and "priority:" in t
        return (ok, "severity + priority set" if ok else "missing sev/pri")
    if assertion_id == "autofail_triggered":
        ok = "auto-fail check: fail" in t
        return (ok, "auto-fail flagged" if ok else "auto-fail not flagged")
    if assertion_id == "overall_zero":
        ok = "weighted score: 0%" in t
        return (ok, "overall 0%" if ok else "overall not 0%")
    if assertion_id == "categories_still_scored":
        ok = "category scores" in t
        return (ok, "categories recorded" if ok else "no category scores")
    if assertion_id == "tag_present":
        ok = "unverified-refund" in t
        return (ok, "tag unverified-refund present" if ok else "tag missing")
    if assertion_id == "not_autofail":
        ok = "auto-fail check: pass" in t
        return (ok, "correctly not an auto-fail" if ok else "wrongly auto-failed")
    if assertion_id == "low_resolution":
        m = re.search(r"resolution \(35%\):\s*([12])\b", t)
        return (m is not None, f"resolution={m.group(1)}" if m else "resolution not 1-2")
    # Judgement-only assertions:
    return (None, "needs human judgement")


def main():
    cases = json.loads((HERE / "eval_cases.json").read_text())
    total = passed = auto = human = 0
    print("=" * 78)
    print("SKILL EVAL GRADING")
    print("=" * 78)
    for skill, out_file in OUT_FILES.items():
        text = (HERE / out_file).read_text()
        print(f"\n### {skill}")
        for c in cases[skill]:
            print(f"  [{c['id']}] {c['name']}")
            for a in c["assertions"]:
                res, ev = check(a["id"], text)
                total += 1
                if res is None:
                    human += 1
                    mark = "· HUMAN"
                elif res:
                    passed += 1; auto += 1
                    mark = "✓ PASS "
                else:
                    auto += 1
                    mark = "✗ FAIL "
                print(f"      {mark} {a['id']}: {ev}")
    print("\n" + "-" * 78)
    print(f"Auto-checkable: {passed}/{auto} passed · {human} assertions flagged for human "
          f"judgement · {total} total")
    return 0 if passed == auto else 1


if __name__ == "__main__":
    raise SystemExit(main())
