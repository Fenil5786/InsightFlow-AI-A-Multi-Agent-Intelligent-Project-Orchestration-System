from typing import Dict, List

import pandas as pd


class DeliveryExecutionAgent:
    name = "DeliveryExecutionAgent"

    def __init__(self, csv_path: str = "data/developer_daily_updates.csv"):
        self.csv_path = csv_path

    def run(self, projects_data: List[Dict[str, str]]) -> Dict[str, object]:
        df = pd.read_csv(self.csv_path)
        df["date"] = pd.to_datetime(df["date"])

        project_names = {p.get("project_name", "") for p in projects_data}
        project_names.discard("")
        if project_names:
            df = df[df["project_name"].isin(project_names)]

        max_date = df["date"].max()
        last_7_days = max_date - pd.Timedelta(days=6)
        last_14_days = max_date - pd.Timedelta(days=13)

        recent_7 = df[df["date"] >= last_7_days]
        recent_14 = df[df["date"] >= last_14_days]

        velocity = (
            recent_7.groupby("project_name")["progress_delta"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        blocker_projects = (
            recent_7[recent_7["blocker"].str.lower() != "none"]
            .groupby("project_name")
            .size()
            .sort_values(ascending=False)
            .head(10)
        )

        contributors = (
            recent_14.groupby("developer")
            .agg(
                total_hours=("hours_spent", "sum"),
                total_progress_delta=("progress_delta", "sum"),
                update_count=("developer", "count"),
            )
            .reset_index()
            .sort_values(by=["total_progress_delta", "total_hours"], ascending=False)
            .head(12)
        )

        blocker_by_dev = (
            recent_14[recent_14["blocker"].str.lower() != "none"]
            .groupby("developer")
            .size()
            .sort_values(ascending=False)
            .head(12)
        )

        return {
            "recent_window_start": str(last_7_days.date()),
            "recent_window_end": str(max_date.date()),
            "top_velocity_projects": [
                {"project_name": k, "weekly_progress_delta": round(float(v), 2)}
                for k, v in velocity.items()
            ],
            "blocker_hotspots": [
                {"project_name": k, "blocker_count": int(v)}
                for k, v in blocker_projects.items()
            ],
            "top_contributors": [
                {
                    "developer": row["developer"],
                    "total_hours": round(float(row["total_hours"]), 1),
                    "total_progress_delta": round(float(row["total_progress_delta"]), 2),
                    "update_count": int(row["update_count"]),
                }
                for _, row in contributors.iterrows()
            ],
            "developer_blocker_counts": [
                {"developer": k, "blocker_count": int(v)}
                for k, v in blocker_by_dev.items()
            ],
            "total_recent_updates": int(len(recent_7)),
        }
