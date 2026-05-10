from typing import Dict, List


def parse_projects(results: List[str]) -> List[Dict[str, str]]:
    projects = []

    for doc in results:
        project = {}

        for line in doc.split("\n"):
            if "Project:" in line:
                project["project_name"] = line.split(":", 1)[1].strip()
            elif "Status:" in line:
                project["status"] = line.split(":", 1)[1].strip()
            elif "Progress:" in line:
                project["progress"] = line.split(":", 1)[1].strip()
            elif "Risk:" in line:
                project["risk_level"] = line.split(":", 1)[1].strip()
            elif "Owner:" in line:
                project["owner"] = line.split(":", 1)[1].strip()
            elif "Last Update:" in line:
                project["last_update"] = line.split(":", 1)[1].strip()

        if project:
            projects.append(project)

    return projects


def progress_to_int(progress_value: str) -> int:
    text = str(progress_value).replace("%", "").strip()
    if not text:
        return 0
    return int(text)
