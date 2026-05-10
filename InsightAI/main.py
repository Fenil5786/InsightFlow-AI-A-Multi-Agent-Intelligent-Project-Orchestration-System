import os

from dotenv import load_dotenv

from orchestrator.insight_orchestrator import run_orchestrator
from tools.email_sender import send_report_email

load_dotenv()

if __name__ == "__main__":
    query = "What is the health of active projects?"
    outputs = run_orchestrator(query)

    recipient = os.getenv("DEFAULT_RECIPIENT_EMAIL", "").strip()
    if not recipient:
        raise ValueError("Set DEFAULT_RECIPIENT_EMAIL in .env to send report email")

    result = send_report_email(
        recipient_email=recipient,
        report_path=outputs["report_path"],
        query=query,
    )
    print(f"Email sent to {result['recipient']}")
