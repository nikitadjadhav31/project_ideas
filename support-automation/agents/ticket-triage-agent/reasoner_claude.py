"""
Live Claude reasoner — drop-in replacement for MockReasoner.

Usage in production:
    from reasoner_claude import ClaudeReasoner
    agent = TriageAgent(reasoner=ClaudeReasoner())

This does NOT change the agent's safety behavior: the deterministic escalation gate in
triage_agent.py still runs before and around this reasoner. The model provides category /
team / urgency judgement for the normal (non-escalation) path and may raise urgency to
"immediate", but it can never lower the deterministic gate's decision.

Requires: `pip install anthropic` and ANTHROPIC_API_KEY in the environment. Left un-imported
by default so the agent runs offline with the mock.
"""

from __future__ import annotations

import json
import os

from triage_agent import Reasoner, Ticket, CATEGORIES, TEAMS

_SYSTEM = """You are a support ticket triage classifier for a SaaS company. Classify the
ticket into exactly one category and route it to one team, and assess urgency.

Valid categories: {categories}
Valid teams: {teams}
Valid urgency levels: low, normal, high, immediate

Rules:
- Choose the single best category for the customer's primary need.
- Map to the most appropriate team.
- An explicit cancellation is an "account" matter (retention), not "billing", even if the
  customer mentions payments.
- A report of something broken or returning wrong results is a "bug".
- Set urgency by customer impact and emotion; reserve "immediate" for things that cannot wait.
- Do NOT attempt to detect outages, security incidents, or legal threats — a separate
  deterministic system handles those. Just classify the ordinary support need.

Respond with ONLY a JSON object, no prose:
{{"category": "...", "team": "...", "urgency": "...", "rationale": "one sentence"}}
""".format(
    categories=", ".join(CATEGORIES),
    teams=", ".join(TEAMS.keys()),
)


class ClaudeReasoner(Reasoner):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic  # imported lazily so the file only needs the SDK when actually used
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model

    def classify(self, ticket: Ticket) -> dict:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=300,
            system=_SYSTEM,
            messages=[{
                "role": "user",
                "content": f"Subject: {ticket.subject}\n\nBody: {ticket.body}",
            }],
        )
        text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
        text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```")
        data = json.loads(text)
        # Defensive validation — never trust the model to stay in-vocabulary.
        if data.get("category") not in CATEGORIES:
            data["category"] = "how_to"
        if data.get("team") not in TEAMS:
            data["team"] = "account"
        if data.get("urgency") not in ("low", "normal", "high", "immediate"):
            data["urgency"] = "normal"
        data.setdefault("rationale", "classified by Claude")
        return data
