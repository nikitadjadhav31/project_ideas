"""
Live Claude synthesizer — drop-in replacement for MockSynthesizer.

Usage in production:
    from synthesizer_claude import ClaudeSynthesizer
    agent = BriefingAgent(synthesizer=ClaudeSynthesizer())

The agent's gather + analyze layers are unchanged: the churn signals are still computed
deterministically in briefing_agent.analyze(). This class only turns those signals + the raw
data into the narrative brief and call talking points. Requires `pip install anthropic` and
ANTHROPIC_API_KEY. Left un-imported by default so the agent runs offline with the mock.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict

from briefing_agent import Synthesizer

_SYSTEM = """You are a customer success analyst. You are given a customer's billing data,
product-usage data, recent support tickets, and a set of pre-computed churn risk signals.

Write a ONE-PAGE retention brief for the CSM before a retention call. Use this structure:
1. Header: company, overall churn risk, renewal date, tenure, plan/MRR/contract value.
2. Risk signals: the signals, most severe first, each one line.
3. Support history: the recent tickets, one line each.
4. Recommended talking points: 3-4 concrete, specific things to raise on the call, derived
   from the strongest signals. Lead with usage/relationship issues, not price.
5. Suggested outcome to aim for.

Hard rules:
- Never invent a refund, discount, credit, or price. Money figures in the data are historical
  record only. If a goodwill gesture is warranted, say to verify it against current policy —
  do NOT state a number.
- Be specific and useful; a CSM should be able to walk into the call from this alone.
- Keep it to roughly one page of markdown.
"""


class ClaudeSynthesizer(Synthesizer):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic
        self._client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
        self._model = model

    def brief(self, ctx: dict) -> str:
        payload = {
            "account_id": ctx["account_id"],
            "billing": ctx["billing"],
            "usage": ctx["usage"],
            "tickets": ctx["tickets"],
            "risk": ctx["risk"],
            "signals": [asdict(s) for s in ctx["signals"]],
        }
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=1500,
            system=_SYSTEM,
            messages=[{
                "role": "user",
                "content": "Write the retention brief from this data:\n\n"
                           + json.dumps(payload, indent=2),
            }],
        )
        return "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
