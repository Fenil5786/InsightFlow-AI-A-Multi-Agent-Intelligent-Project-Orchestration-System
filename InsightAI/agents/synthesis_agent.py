import json
from typing import Dict

from agents.llm_client import client


class SynthesisAgent:
    name = "SynthesisAgent"

    def run(
        self,
        query: str,
        intent: str,
        outputs: Dict[str, object],
        data_text: str,
        focus_hint: str = "",
        critic_hint: str = "",
    ) -> str:
        prompt = f"""
You are SynthesisAgent, the final agent in a multi-agent delivery intelligence workflow.

User Question:
{query}

Detected Intent:
{intent}

Agent Outputs (JSON):
{json.dumps(outputs, indent=2)}

Planner Focus Hint:
{focus_hint or "None"}

Critic Feedback from prior attempt:
{critic_hint or "None"}

STRICT RULES:
- Use agent outputs as primary evidence.
- Only use raw data to add supporting details.
- Return only one response type based on intent:
  - summary: bullet points only
  - health: risk %, avg progress, health statement
  - active: list of active work only
  - risk: risky projects and reasons
  - action: 3-5 concrete actions

Raw Data:
{data_text}
"""

        return client.complete(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
