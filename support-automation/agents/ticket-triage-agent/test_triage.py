"""
Tests for the triage agent. The critical property under test: the deterministic escalation
gate NEVER misses an outage / security / legal trigger, regardless of what the reasoner says.

Run: python3 test_triage.py
"""

from triage_agent import Ticket, TriageAgent, MockReasoner, deterministic_gate


def t(body, subject="(subj)"):
    return Ticket(id="TEST", subject=subject, body=body, customer="c", received_at="now")


class AlwaysHowToReasoner(MockReasoner):
    """Adversarial reasoner that always says 'how_to' — to prove the gate is independent."""
    def classify(self, ticket):
        return {"category": "how_to", "team": "onboarding",
                "urgency": "low", "rationale": "adversarial: always how_to"}


def test_gate_catches_escalations_even_with_adversarial_reasoner():
    agent = TriageAgent(reasoner=AlwaysHowToReasoner())
    cases = {
        "everything is down for the whole team": ("outage", "engineering"),
        "I think we had a data breach": ("security", "security"),
        "my attorney will be in touch about a lawsuit": ("legal", "legal"),
        "this is a GDPR data deletion request": ("legal", "legal"),
        "unauthorized access to my account": ("security", "security"),
    }
    for body, (exp_cat, exp_team) in cases.items():
        d = agent.handle(t(body))
        assert d.escalated, f"MISSED escalation: {body!r}"
        assert d.category == exp_cat, f"{body!r}: got {d.category}, want {exp_cat}"
        assert d.team == exp_team, f"{body!r}: got {d.team}, want {exp_team}"
        assert d.urgency == "immediate"
        assert d.source == "deterministic-gate"
    print("PASS: gate catches all escalations even with an adversarial reasoner")


def test_normal_tickets_not_escalated():
    agent = TriageAgent(reasoner=MockReasoner())
    for body in ["how do I invite a teammate?",
                 "I was double charged on my invoice",
                 "the csv export is broken",
                 "it would be nice to have dark mode"]:
        d = agent.handle(t(body))
        assert not d.escalated, f"false escalation on: {body!r}"
        assert d.source == "reasoner"
    print("PASS: ordinary tickets route via the reasoner without escalation")


def test_gate_is_pure_function():
    # No reasoner involved: the gate stands alone and is deterministic.
    assert deterministic_gate(t("service is down")) is not None
    assert deterministic_gate(t("how do I export data?")) is None
    # Same input -> same output, twice.
    a = deterministic_gate(t("we were hacked"))
    b = deterministic_gate(t("we were hacked"))
    assert a == b
    print("PASS: deterministic gate is a pure, repeatable function")


def test_cancellation_beats_billing():
    agent = TriageAgent(reasoner=MockReasoner())
    d = agent.handle(t("please cancel my subscription, I'm done paying for this"))
    assert d.category == "account", f"cancellation misrouted to {d.category}"
    print("PASS: explicit cancellation routes to account (retention), not billing")


if __name__ == "__main__":
    test_gate_catches_escalations_even_with_adversarial_reasoner()
    test_normal_tickets_not_escalated()
    test_gate_is_pure_function()
    test_cancellation_beats_billing()
    print("\nAll triage tests passed.")
