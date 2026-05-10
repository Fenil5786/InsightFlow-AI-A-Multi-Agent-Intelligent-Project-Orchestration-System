import json
from typing import Dict, List

from agents.llm_client import client


class CriticAgent:
    name = "CriticAgent"

    def run(self, query: str, intent: str, response_text: str, used_agents: List[str]) -> Dict[str, object]:
        prompt = f"""
You are CriticAgent in an autonomous multi-agent workflow.
Evaluate if the answer is complete for the query and intent.
Return strict JSON only.

Query: {query}
Intent: {intent}
Used agents: {used_agents}

Answer:
{response_text}

JSON schema:
{{
  "score": 0,
  "pass": false,
  "issues": ["short issue 1", "short issue 2"],
  "improvement_hint": "single sentence"
}}

Rules:
- score range 0..100
- pass true only if score >= 75
- issues must be specific
"""

        try:
            text = client.complete(
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            result = json.loads(text)

            score = int(result.get("score", 0))
            passed = bool(result.get("pass", False))
            issues = [str(i) for i in result.get("issues", [])][:5]
            hint = str(result.get("improvement_hint", ""))

            return {
                "score": max(0, min(100, score)),
                "pass": passed if score >= 75 else False,
                "issues": issues,
                "improvement_hint": hint,
            }
        except Exception:
            return self._fallback_review(response_text)

    def _fallback_review(self, response_text: str) -> Dict[str, object]:
        text = response_text.strip()
        if len(text) < 120:
            return {
                "score": 45,
                "pass": False,
                "issues": ["Response is too short for confident decision support."],
                "improvement_hint": "Provide more specific evidence and actions.",
            }

        return {
            "score": 78,
            "pass": True,
            "issues": [],
            "improvement_hint": "",
        }
