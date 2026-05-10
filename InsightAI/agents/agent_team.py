from typing import Dict, List

from agents.critic_agent import CriticAgent
from agents.delivery_execution_agent import DeliveryExecutionAgent
from agents.planner_agent import PlannerAgent
from agents.portfolio_agent import PortfolioAgent
from agents.synthesis_agent import SynthesisAgent


def run_agent_team(query: str, projects_data: List[Dict[str, str]], data_text: str) -> str:
    planner_agent = PlannerAgent()
    critic_agent = CriticAgent()
    portfolio_agent = PortfolioAgent()
    delivery_execution_agent = DeliveryExecutionAgent()
    synthesis_agent = SynthesisAgent()

    available_agents = {
        "portfolio_agent": lambda: portfolio_agent.run(projects_data),
        "delivery_execution_agent": lambda: delivery_execution_agent.run(projects_data),
    }

    max_attempts = 3
    previous_feedback: List[str] = []
    best_response = ""
    best_review = {"score": -1, "pass": False, "issues": [], "improvement_hint": ""}
    final_intent = "summary"

    for attempt_number in range(1, max_attempts + 1):
        plan = planner_agent.run(query=query, intent=final_intent, previous_feedback=previous_feedback)
        final_intent = str(plan.get("intent", final_intent)).lower()
        selected_agents = [a for a in plan.get("selected_agents", []) if a in available_agents]
        if not selected_agents:
            selected_agents = ["portfolio_agent", "delivery_execution_agent"]

        outputs = {agent_name: available_agents[agent_name]() for agent_name in selected_agents}

        final_response = synthesis_agent.run(
            query=query,
            intent=final_intent,
            outputs=outputs,
            data_text=data_text,
            focus_hint=str(plan.get("focus", "")),
            critic_hint="; ".join(previous_feedback),
        )

        review = critic_agent.run(
            query=query,
            intent=final_intent,
            response_text=final_response,
            used_agents=selected_agents,
        )

        if review.get("score", 0) > best_review.get("score", -1):
            best_review = review
            best_response = final_response

        if review.get("pass", False):
            break

        previous_feedback = list(review.get("issues", []))
        hint = str(review.get("improvement_hint", "")).strip()
        if hint:
            previous_feedback.append(hint)

    return best_response
