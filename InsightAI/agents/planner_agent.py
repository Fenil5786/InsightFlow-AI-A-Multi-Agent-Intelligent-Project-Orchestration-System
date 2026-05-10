import json
from typing import Dict, List, Optional

from agents.llm_client import client


AVAILABLE_AGENTS = [
    "portfolio_agent",
    "delivery_execution_agent",
]


class PlannerAgent:
    name = "PlannerAgent"

    def run(self, query: str, intent: Optional[str] = None, previous_feedback: Optional[List[str]] = None) -> Dict[str, object]:
        detected_intent = intent or self._detect_intent(query)
        feedback_text = "\n".join(previous_feedback or []) or "None"

        prompt = f"""
You are PlannerAgent in an autonomous multi-agent system.
Return strict JSON only.

Task:
- Build an execution plan for this query.
- Choose only from these agent ids:
  {AVAILABLE_AGENTS}
- Keep selected_agents between 1 and 2.
- Provide concise reasoning.

Query: {query}
Intent: {detected_intent}
Previous critic feedback:
{feedback_text}

JSON schema:
{{
    "intent": "summary",
    "selected_agents": ["portfolio_agent", "delivery_execution_agent"],
  "reasoning": "short reason",
  "focus": "what synthesis should emphasize"
}}
"""

        try:
            text = client.complete(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            plan = json.loads(text)
            selected = [a for a in plan.get("selected_agents", []) if a in AVAILABLE_AGENTS]
            if len(selected) < 1:
                raise ValueError("Planner returned too few agents")
            if len(selected) > 2:
                selected = selected[:2]

            plan_intent = str(plan.get("intent", detected_intent)).strip().lower()
            if plan_intent not in {"summary", "health", "active", "risk", "action"}:
                plan_intent = detected_intent

            return {
                "intent": plan_intent,
                "selected_agents": selected,
                "reasoning": str(plan.get("reasoning", "")),
                "focus": str(plan.get("focus", "")),
            }
        except Exception:
            return self._fallback_plan(detected_intent, previous_feedback)

    def _fallback_plan(self, intent: str, previous_feedback: Optional[List[str]]) -> Dict[str, object]:
        if intent == "active":
            selected = ["portfolio_agent"]
            focus = "active project list and ownership"
        elif intent == "risk":
            selected = ["portfolio_agent", "delivery_execution_agent"]
            focus = "risk concentration and blocker-driven causes"
        elif intent == "action":
            selected = ["portfolio_agent", "delivery_execution_agent"]
            focus = "portfolio facts plus execution trend to derive actions"
        else:
            selected = ["portfolio_agent", "delivery_execution_agent"]
            focus = "portfolio health with execution trend and accountability"

        if previous_feedback:
            if "insufficient evidence" in " ".join(previous_feedback).lower() and "delivery_execution_agent" not in selected:
                selected.append("delivery_execution_agent")

        return {
            "intent": intent,
            "selected_agents": selected,
            "reasoning": "Fallback plan from intent rules.",
            "focus": focus,
        }

    def _detect_intent(self, query: str) -> str:
        q = query.lower()
        if "risk" in q:
            return "risk"
        if "active" in q:
            return "active"
        if "health" in q:
            return "health"
        if "action" in q or "recommend" in q:
            return "action"
        return "summary"
