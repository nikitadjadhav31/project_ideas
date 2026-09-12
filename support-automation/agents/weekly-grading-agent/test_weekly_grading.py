"""
Tests for the weekly grading agent.

Run: python3 test_weekly_grading.py
"""

from weekly_grading_agent import (
    ClosedTicket, WeeklyGradingAgent, MockGrader, RollingSampler, WEIGHTS,
)


def tk(id, msg, reply, agent="dev", cat="billing"):
    return ClosedTicket(id=id, closed_at="2026-09-01", category=cat,
                        assigned_agent=agent, customer_message=msg, agent_reply=reply)


def test_sampling_is_deterministic_under_seed():
    pool = [tk(f"C-{i}", "hi", "there") for i in range(50)]
    s1 = RollingSampler(sample_size=10, seed=7).sample(pool)
    s2 = RollingSampler(sample_size=10, seed=7).sample(pool)
    assert [t.id for t in s1] == [t.id for t in s2], "same seed must give same sample"
    s3 = RollingSampler(sample_size=10, seed=8).sample(pool)
    assert [t.id for t in s1] != [t.id for t in s3], "different seed should differ"
    assert len(s1) == 10
    print("PASS: sampling is deterministic under a seed, varies across seeds")


def test_sample_smaller_than_size_returns_all():
    pool = [tk("C-1", "hi", "there"), tk("C-2", "hi", "there")]
    s = RollingSampler(sample_size=10, seed=1).sample(pool)
    assert len(s) == 2
    print("PASS: sample of a small pool returns everything")


def test_auto_fail_unverified_money():
    g = MockGrader().grade(tk("C-x", "was I overcharged?",
                              "Yes, I've confirmed a $150 refund, back in 3-5 days."))
    assert g.auto_fail == "unverified_money_claim"
    assert g.weighted_score == 0
    assert "unverified-refund" in g.failure_tags
    assert g.scores, "category scores still recorded for coaching"
    print("PASS: unverified money claim auto-fails at 0% with scores retained")


def test_auto_fail_missed_escalation():
    g = MockGrader().grade(tk("C-y", "our whole team can't log in, app won't load",
                              "Have you tried clearing your cache?"))
    assert g.auto_fail == "missed_mandatory_escalation"
    assert g.weighted_score == 0
    print("PASS: outage answered instead of escalated auto-fails")


def test_escalation_handled_is_not_autofail():
    g = MockGrader().grade(tk("C-z", "the whole site is down",
                              "This is a full outage - I've escalated to engineering on-call "
                              "now and I'll update you within 30 minutes."))
    assert g.auto_fail is None, "escalating an outage should NOT auto-fail"
    print("PASS: correctly escalated outage is not an auto-fail")


def test_weights_sum_to_one():
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9
    print("PASS: rubric weights sum to 1.0")


def test_good_reply_scores_high_and_passes():
    g = MockGrader().grade(tk(
        "C-good", "how do I invite a teammate?",
        "Go to Settings > Members > Invite, enter their email and pick a role. I'll follow up "
        "if you need anything else.", cat="how_to"))
    assert g.weighted_score >= 80
    assert g.passed
    print(f"PASS: a solid reply scores high ({g.weighted_score}%) and passes clean")


def test_tagged_reply_not_counted_as_clean_pass():
    # A reply that hits >=80 but carries a failure tag must NOT be a clean pass.
    g = MockGrader().grade(tk("C-vague", "dashboard is slow",
                              "Sorry about that. Someone will look into it shortly.", cat="bug"))
    if g.weighted_score >= 80:
        assert not g.passed, "a tagged (vague-timeline) reply should not be a clean pass"
    print(f"PASS: tagged reply ({g.weighted_score}%, tags={g.failure_tags}) not a clean pass")


def test_synthesis_flags_offending_agent_and_patterns():
    pool = [
        tk("C-1", "overcharged?", "Yes, $150 refund coming.", agent="dev"),          # auto-fail
        tk("C-2", "site is down", "try clearing cache", agent="dev"),                  # auto-fail
        tk("C-3", "how do I export?", "Go to Settings > Data > Export.", agent="ana", cat="how_to"),
        tk("C-4", "invite a teammate?", "Settings > Members > Invite, pick a role.", agent="ana", cat="how_to"),
    ]
    report = WeeklyGradingAgent(sampler=RollingSampler(sample_size=10, seed=1)).run(pool)
    assert report.auto_fail_rate == 50.0
    assert "dev" in report.per_agent and report.per_agent["dev"]["auto_fails"] == 2
    assert "dev" in report.narrative
    # the strong agent should not be flagged for coaching
    assert report.per_agent["ana"]["mean"] > report.per_agent["dev"]["mean"]
    print("PASS: synthesis flags the offending agent and computes per-agent stats")


if __name__ == "__main__":
    test_sampling_is_deterministic_under_seed()
    test_sample_smaller_than_size_returns_all()
    test_auto_fail_unverified_money()
    test_auto_fail_missed_escalation()
    test_escalation_handled_is_not_autofail()
    test_weights_sum_to_one()
    test_good_reply_scores_high_and_passes()
    test_tagged_reply_not_counted_as_clean_pass()
    test_synthesis_flags_offending_agent_and_patterns()
    print("\nAll weekly-grading tests passed.")
