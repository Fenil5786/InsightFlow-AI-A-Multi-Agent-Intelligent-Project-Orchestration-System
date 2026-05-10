# orchestrator/insight_orchestrator.py

from agents.agent_team import run_agent_team
from agents.project_parser import parse_projects as parse_project_docs
from rag.embedding_pipeline import hybrid_search
from ui.report_template import build_industry_report

# -----------------------------
# STEP 1: GET DATA
# -----------------------------
def get_project_data(query):
    results = hybrid_search(query)
    return results


# -----------------------------
# STEP 3: MULTI-AGENT INSIGHT GENERATION
# -----------------------------
def generate_agentic_insights(query, projects_data, data_text):
    return run_agent_team(query, projects_data, data_text)


# -----------------------------
# MAIN FLOW
def run_orchestrator(query):

    raw_data      = get_project_data(query)
    projects_data = parse_project_docs(raw_data)
    data_text     = "\n\n".join(raw_data)
    insights = generate_agentic_insights(query, projects_data, data_text)
    html_report   = build_industry_report(insights, projects_data)

    with open("report.html", "w", encoding="utf-8") as f:
        f.write(html_report)

    print("Report generated → report.html")

    return {
        "report_path": "report.html",
    }


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":
    query = "What is the health of active projects?"
    run_orchestrator(query)
