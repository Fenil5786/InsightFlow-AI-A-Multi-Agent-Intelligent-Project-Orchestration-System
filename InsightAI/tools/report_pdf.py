import importlib
from pathlib import Path

def generate_pdf_from_html(report_html_path: str, pdf_path: str = "report.pdf") -> str:
    html_file = Path(report_html_path).resolve()
    if not html_file.exists():
        raise FileNotFoundError(f"Report HTML not found: {report_html_path}")

    output = Path(pdf_path).resolve()

    try:
        sync_api = importlib.import_module("playwright.sync_api")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "PDF generation requires Playwright. Install with: pip install playwright "
            "and then run: playwright install chromium"
        ) from exc

    try:
        with sync_api.sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 2200})
            page.goto(html_file.as_uri(), wait_until="networkidle")
            page.emulate_media(media="screen")
            page.pdf(
                path=str(output),
                format="A4",
                print_background=True,
                margin={"top": "12mm", "right": "10mm", "bottom": "12mm", "left": "10mm"},
            )
            browser.close()
    except Exception as exc:
        message = str(exc)
        if "playwright install" in message.lower() or "executable doesn't exist" in message.lower():
            raise RuntimeError(
                "Playwright browser binaries are missing. Run: playwright install chromium"
            ) from exc
        raise

    return str(output)
