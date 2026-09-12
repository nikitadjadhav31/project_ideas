"""
Tests for the at-risk briefing agent.

Run: python3 test_briefing.py
"""

import re

from briefing_agent import (
    BriefingAgent, analyze, overall_risk, BillingConnector, UsageConnector, TicketsConnector,
)


def test_gathers_from_all_three_systems():
    agent = BriefingAgent()
    g = agent.gather("acme-corp")
    assert g["billing"] and g["usage"] and g["tickets"], "should pull from all three systems"
    assert g["billing"]["company_name"] == "Acme Corp"
    print("PASS: gathers billing + usage + tickets for a known account")


def test_high_risk_account_scores_high():
    agent = BriefingAgent()
    g = agent.gather("acme-corp")
    signals = analyze(g["billing"], g["usage"], g["tickets"])
    assert overall_risk(signals) == "HIGH"
    # Must catch the severe usage collapse and low seat utilization.
    labels = {s.label for s in signals}
    assert "Active-seat trend" in labels
    assert "Seat utilization" in labels
    print("PASS: collapsing account is scored HIGH with the right signals")


def test_healthy_account_scores_low_or_medium():
    agent = BriefingAgent()
    g = agent.gather("globex-llc")
    signals = analyze(g["billing"], g["usage"], g["tickets"])
    risk = overall_risk(signals)
    assert risk in ("LOW", "MEDIUM"), f"healthy account scored {risk}"
    print(f"PASS: healthy account scored {risk} (not HIGH)")


def test_recurring_defect_detected_from_explicit_signal():
    agent = BriefingAgent()
    g = agent.gather("acme-corp")
    signals = analyze(g["billing"], g["usage"], g["tickets"])
    assert any(s.label == "Recurring defect" for s in signals), \
        "should flag the explicitly-'again' reporting bug as recurring"
    print("PASS: recurring defect detected from explicit repeat signal")


def test_brief_never_states_invented_money_figure():
    # The brief may cite historical billing figures, but must not fabricate an offer amount.
    # Guard: no "$<n> refund/discount/credit/off" style promise appears.
    agent = BriefingAgent()
    brief = agent.run("acme-corp")
    bad = re.search(r"\$\s?\d[\d,]*\s*(refund|discount|credit|off\b)", brief, re.I)
    assert bad is None, f"brief promised a money figure: {bad.group(0)!r}"
    assert "verify" in brief.lower()  # it should tell the CSM to verify offers against policy
    print("PASS: brief cites no invented refund/discount figure and defers to policy")


def test_unknown_account_degrades_gracefully():
    agent = BriefingAgent()
    brief = agent.run("does-not-exist")
    assert "No data found" in brief
    print("PASS: unknown account degrades gracefully")


if __name__ == "__main__":
    test_gathers_from_all_three_systems()
    test_high_risk_account_scores_high()
    test_healthy_account_scores_low_or_medium()
    test_recurring_defect_detected_from_explicit_signal()
    test_brief_never_states_invented_money_figure()
    test_unknown_account_degrades_gracefully()
    print("\nAll briefing tests passed.")
