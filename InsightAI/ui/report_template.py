from datetime import datetime
from html import escape
from typing import Dict, List

import markdown


def _progress_to_int(value: str) -> int:
    text = str(value).replace("%", "").strip()
    if not text:
        return 0
    try:
        return int(text)
    except ValueError:
        return 0


def _badge_class(risk_level: str) -> str:
    risk = risk_level.lower()
    if risk == "high":
        return "risk-high"
    if risk == "medium":
        return "risk-medium"
    return "risk-low"


def _health_label(score: int) -> str:
    if score >= 75:
        return "Healthy"
    if score >= 50:
        return "Watch"
    return "Critical"


def build_industry_report(insights: str, projects_data: List[Dict[str, str]]) -> str:
    total = len(projects_data)
    high = sum(1 for p in projects_data if p.get("risk_level", "").lower() == "high")
    medium = sum(1 for p in projects_data if p.get("risk_level", "").lower() == "medium")
    low = sum(1 for p in projects_data if p.get("risk_level", "").lower() == "low")

    progress_values = [_progress_to_int(p.get("progress", "0")) for p in projects_data]
    avg_progress = round(sum(progress_values) / len(progress_values)) if progress_values else 0

    raw_health = 100 - (high * 12) - (medium * 5) + (avg_progress * 0.35)
    health_score = max(0, min(100, round(raw_health)))
    health_label = _health_label(health_score)

    generated_at = datetime.now().strftime("%d %b %Y, %I:%M %p")

    top_risks = sorted(
        projects_data,
        key=lambda p: (_progress_to_int(p.get("progress", "0")), p.get("risk_level", "")),
    )[:8]

    rows = []
    for idx, p in enumerate(sorted(projects_data, key=lambda x: _progress_to_int(x.get("progress", "0"))), start=1):
        name = escape(p.get("project_name", "Unknown"))
        owner = escape(p.get("owner", "Unknown"))
        status = escape(p.get("status", "Unknown"))
        risk = escape(p.get("risk_level", "Low"))
        progress = _progress_to_int(p.get("progress", "0"))
        badge = _badge_class(risk)
        bar_class = "bar-green" if progress >= 70 else "bar-amber" if progress >= 45 else "bar-red"

        rows.append(
            f"""
            <tr>
                <td>{idx}</td>
                <td>{name}</td>
                <td>{owner}</td>
                <td>{status}</td>
                <td><span class=\"risk-pill {badge}\">{risk}</span></td>
                <td>
                    <div class=\"progress-cell\">
                        <div class=\"progress-track\"><div class=\"progress-fill {bar_class}\" style=\"width:{progress}%\"></div></div>
                        <span>{progress}%</span>
                    </div>
                </td>
            </tr>
            """
        )

    risk_rows = []
    for p in top_risks:
        risk_rows.append(
            f"<li><strong>{escape(p.get('project_name', 'Unknown'))}</strong> - {escape(p.get('risk_level', 'Low'))} risk, {escape(str(p.get('progress', '0%')))} complete</li>"
        )

    insights_html = markdown.markdown(insights, extensions=["tables", "fenced_code"])

    return f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>Delivery Portfolio Intelligence Report</title>
    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">
    <style>
        :root {{
            --bg: #f3f6fb;
            --surface: #ffffff;
            --surface-2: #f9fbff;
            --ink: #0f1b2d;
            --muted: #5f6f86;
            --line: #d8e2ef;
            --primary: #0a5bd8;
            --primary-soft: #e7f0ff;
            --green: #1a9d6f;
            --amber: #d9822b;
            --red: #d3425f;
            --radius: 16px;
        }}

        * {{ box-sizing: border-box; }}

        body {{
            margin: 0;
            background: linear-gradient(160deg, #eef4ff 0%, #f9fbff 45%, #f2f6fb 100%);
            color: var(--ink);
            font-family: 'Manrope', sans-serif;
        }}

        .container {{
            max-width: 1240px;
            margin: 0 auto;
            padding: 28px 18px 36px;
        }}

        .hero {{
            background: radial-gradient(circle at 85% 15%, rgba(38, 121, 255, 0.12), transparent 46%), var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 22px;
            box-shadow: 0 10px 30px rgba(27, 57, 98, 0.08);
            display: grid;
            gap: 10px;
        }}

        .hero h1 {{
            margin: 0;
            font-size: clamp(1.2rem, 2vw, 1.9rem);
            letter-spacing: 0.01em;
        }}

        .hero-meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            color: var(--muted);
            font-size: 0.9rem;
        }}

        .kpi-grid {{
            margin-top: 18px;
            display: grid;
            grid-template-columns: repeat(5, minmax(140px, 1fr));
            gap: 12px;
        }}

        .kpi {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: 12px;
            padding: 12px;
        }}

        .kpi-label {{
            color: var(--muted);
            font-size: 0.8rem;
            margin-bottom: 6px;
        }}

        .kpi-value {{
            font-size: 1.35rem;
            font-weight: 800;
            line-height: 1.1;
        }}

        .health-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            font-size: 0.76rem;
            font-weight: 700;
            background: var(--primary-soft);
            color: var(--primary);
        }}

        .layout {{
            margin-top: 18px;
            display: grid;
            grid-template-columns: 1.4fr 1fr;
            gap: 14px;
        }}

        .panel {{
            background: var(--surface);
            border: 1px solid var(--line);
            border-radius: var(--radius);
            padding: 16px;
        }}

        .panel h2, .panel h3 {{
            margin: 0 0 12px;
            font-size: 1rem;
        }}

        .insights-content {{
            color: #203047;
            line-height: 1.62;
            font-size: 0.94rem;
        }}

        .risk-list {{
            margin: 0;
            padding-left: 18px;
            color: #1f2e44;
            line-height: 1.55;
            font-size: 0.92rem;
        }}

        .risk-bars {{
            display: grid;
            gap: 10px;
            margin-top: 10px;
        }}

        .risk-bar-item {{
            display: grid;
            grid-template-columns: 76px 1fr 44px;
            align-items: center;
            gap: 8px;
            font-size: 0.86rem;
        }}

        .risk-track {{
            height: 9px;
            border-radius: 999px;
            background: #edf2f9;
            overflow: hidden;
        }}

        .risk-fill {{ height: 100%; border-radius: 999px; }}
        .high-fill {{ background: var(--red); }}
        .medium-fill {{ background: var(--amber); }}
        .low-fill {{ background: var(--green); }}

        .panel-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            margin-bottom: 10px;
        }}

        .intent {{
            font-size: 0.78rem;
            color: var(--primary);
            background: var(--primary-soft);
            padding: 4px 9px;
            border-radius: 999px;
            font-weight: 700;
        }}

        .chips {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }}

        .chip {{
            border: 1px solid var(--line);
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 0.78rem;
            color: #30445f;
            background: var(--surface-2);
        }}

        .table-panel {{ margin-top: 14px; }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}

        thead th {{
            text-align: left;
            color: #46607f;
            background: #f2f6fd;
            border-bottom: 1px solid var(--line);
            padding: 10px;
            font-weight: 700;
        }}

        tbody td {{
            border-bottom: 1px solid #edf2f8;
            padding: 10px;
            vertical-align: middle;
            color: #24364c;
        }}

        .risk-pill {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
        }}

        .risk-high {{ background: #ffe9ee; color: #ad2944; }}
        .risk-medium {{ background: #fff2e3; color: #a25a13; }}
        .risk-low {{ background: #e8faf2; color: #167a56; }}

        .progress-cell {{
            display: grid;
            grid-template-columns: 1fr auto;
            align-items: center;
            gap: 8px;
            min-width: 140px;
        }}

        .progress-track {{
            height: 8px;
            border-radius: 999px;
            background: #e7eef7;
            overflow: hidden;
        }}

        .progress-fill {{ height: 100%; border-radius: 999px; }}
        .bar-green {{ background: var(--green); }}
        .bar-amber {{ background: var(--amber); }}
        .bar-red {{ background: var(--red); }}

        .footer {{
            margin-top: 14px;
            color: var(--muted);
            font-family: 'IBM Plex Mono', monospace;
            font-size: 0.74rem;
        }}

        @media (max-width: 1080px) {{
            .kpi-grid {{ grid-template-columns: repeat(3, minmax(140px, 1fr)); }}
            .layout {{ grid-template-columns: 1fr; }}
        }}

        @media (max-width: 700px) {{
            .kpi-grid {{ grid-template-columns: repeat(2, minmax(130px, 1fr)); }}
            .container {{ padding: 16px 12px 22px; }}
            table {{ font-size: 0.8rem; }}
            thead th, tbody td {{ padding: 8px; }}
        }}
    </style>
</head>
<body>
    <div class=\"container\">
        <section class=\"hero\">
            <h1>Delivery Portfolio Intelligence Report</h1>
            <div class=\"hero-meta\">
                <span>Generated: {escape(generated_at)}</span>
                <span>Coverage: {total} Projects</span>
                <span class=\"health-chip\">Health {health_score}/100 ({health_label})</span>
            </div>
        </section>

        <section class=\"kpi-grid\">
            <article class=\"kpi\"><div class=\"kpi-label\">Total Projects</div><div class=\"kpi-value\">{total}</div></article>
            <article class=\"kpi\"><div class=\"kpi-label\">Avg Progress</div><div class=\"kpi-value\">{avg_progress}%</div></article>
            <article class=\"kpi\"><div class=\"kpi-label\">High Risk</div><div class=\"kpi-value\" style=\"color:var(--red)\">{high}</div></article>
            <article class=\"kpi\"><div class=\"kpi-label\">Medium Risk</div><div class=\"kpi-value\" style=\"color:var(--amber)\">{medium}</div></article>
            <article class=\"kpi\"><div class=\"kpi-label\">Low Risk</div><div class=\"kpi-value\" style=\"color:var(--green)\">{low}</div></article>
        </section>

        <section class=\"layout\">
            <article class=\"panel\">
                <h2>Executive Insights</h2>
                <div class=\"insights-content\">{insights_html}</div>
            </article>

            <aside class=\"panel\">
                <h3>Risk Concentration</h3>
                <div class=\"risk-bars\">
                    <div class=\"risk-bar-item\"><span>High</span><div class=\"risk-track\"><div class=\"risk-fill high-fill\" style=\"width:{0 if total == 0 else round((high/total)*100)}%\"></div></div><span>{high}</span></div>
                    <div class=\"risk-bar-item\"><span>Medium</span><div class=\"risk-track\"><div class=\"risk-fill medium-fill\" style=\"width:{0 if total == 0 else round((medium/total)*100)}%\"></div></div><span>{medium}</span></div>
                    <div class=\"risk-bar-item\"><span>Low</span><div class=\"risk-track\"><div class=\"risk-fill low-fill\" style=\"width:{0 if total == 0 else round((low/total)*100)}%\"></div></div><span>{low}</span></div>
                </div>
                <h3 style=\"margin-top:14px;\">Top Watchlist</h3>
                <ul class=\"risk-list\">{''.join(risk_rows)}</ul>
            </aside>
        </section>

        <section class=\"panel table-panel\">
            <div class=\"panel-head\">
                <h3>Project Portfolio Detail</h3>
                <span class=\"intent\">Sorted by Lowest Progress</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Project</th>
                        <th>Owner</th>
                        <th>Status</th>
                        <th>Risk</th>
                        <th>Progress</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(rows)}
                </tbody>
            </table>
        </section>

        <div class=\"footer\">Data sources: RAG project corpus + developer daily updates</div>
    </div>
</body>
</html>"""
