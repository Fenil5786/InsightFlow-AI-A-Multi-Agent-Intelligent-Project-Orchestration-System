from typing import Dict, List

from agents.project_parser import progress_to_int


class PortfolioAgent:
    name = "PortfolioAgent"

    def run(self, projects_data: List[Dict[str, str]]) -> Dict[str, object]:
        active = [p for p in projects_data if p.get("status", "").lower() == "active"]
        completed = [p for p in projects_data if p.get("status", "").lower() == "completed"]

        high_risk = [p for p in projects_data if p.get("risk_level", "").lower() == "high"]
        medium_risk = [p for p in projects_data if p.get("risk_level", "").lower() == "medium"]

        progress_values = [progress_to_int(p.get("progress", "0")) for p in projects_data]
        avg_progress = round(sum(progress_values) / len(progress_values)) if progress_values else 0

        lagging = sorted(
            [p for p in projects_data if progress_to_int(p.get("progress", "0")) < 60],
            key=lambda p: progress_to_int(p.get("progress", "0")),
        )[:10]

        owner_summary = {}
        for p in projects_data:
            owner = p.get("owner", "Unknown")
            owner_summary.setdefault(owner, {"total": 0, "high_risk": 0, "progress": []})
            owner_summary[owner]["total"] += 1
            owner_summary[owner]["progress"].append(progress_to_int(p.get("progress", "0")))
            if p.get("risk_level", "").lower() == "high":
                owner_summary[owner]["high_risk"] += 1

        owners = []
        for owner, info in owner_summary.items():
            owner_avg = round(sum(info["progress"]) / len(info["progress"])) if info["progress"] else 0
            owners.append(
                {
                    "owner": owner,
                    "project_count": info["total"],
                    "high_risk_count": info["high_risk"],
                    "avg_progress": owner_avg,
                }
            )

        owners.sort(key=lambda x: (-x["high_risk_count"], x["avg_progress"]))

        top_high_risk = sorted(high_risk, key=lambda p: progress_to_int(p.get("progress", "0")))[:10]

        return {
            "active_count": len(active),
            "completed_count": len(completed),
            "high_risk_count": len(high_risk),
            "medium_risk_count": len(medium_risk),
            "avg_progress": avg_progress,
            "lagging_projects": [
                {
                    "project_name": p.get("project_name", "Unknown"),
                    "progress": p.get("progress", "0%"),
                }
                for p in lagging
            ],
            "top_high_risk": [
                {
                    "project_name": p.get("project_name", "Unknown"),
                    "progress": p.get("progress", "0%"),
                    "owner": p.get("owner", "Unknown"),
                }
                for p in top_high_risk
            ],
            "owner_summary": owners[:10],
        }
