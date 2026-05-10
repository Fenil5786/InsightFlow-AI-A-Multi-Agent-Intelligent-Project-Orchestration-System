import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv
from tools.report_pdf import generate_pdf_from_html

load_dotenv()


def _env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Missing required environment variable: {name}")
    value = value.strip()
    if value == "":
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def send_report_email(
    recipient_email: str,
    report_path: str = "report.html",
    query: str = "",
    pdf_path: str = "report.pdf",
) -> Dict[str, str]:
    smtp_host = _env("SMTP_HOST")
    smtp_port = int(_env("SMTP_PORT", "587"))
    smtp_username = _env("SMTP_USERNAME")
    smtp_password = _env("SMTP_PASSWORD")
    sender_email = _env("SMTP_SENDER_EMAIL", smtp_username)
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    if "@" not in smtp_username and "@" in sender_email:
        smtp_username = sender_email

    report_file = Path(report_path)
    if not report_file.exists():
        raise FileNotFoundError(f"Report file not found: {report_path}")

    generated_pdf_path = generate_pdf_from_html(str(report_file), pdf_path)
    pdf_file = Path(generated_pdf_path)

    report_html = report_file.read_text(encoding="utf-8")
    subject = "Delivery Portfolio Intelligence Report"

    if query.strip():
        subject = f"Delivery Report: {query.strip()[:80]}"

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    message.set_content(
        "Please find the latest delivery intelligence report attached as PDF. "
        "An HTML preview is also included in this email body."
    )
    message.add_alternative(report_html, subtype="html")

    message.add_attachment(
        pdf_file.read_bytes(),
        maintype="application",
        subtype="pdf",
        filename=pdf_file.name,
    )

    with smtplib.SMTP(smtp_host, smtp_port) as smtp:
        if use_tls:
            smtp.starttls()
        smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)

    return {
        "status": "sent",
        "recipient": recipient_email,
        "subject": subject,
        "pdf_attachment": pdf_file.name,
    }
