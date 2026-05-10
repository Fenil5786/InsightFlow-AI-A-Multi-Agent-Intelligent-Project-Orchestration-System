# ui/app.py

import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from orchestrator.insight_orchestrator import run_orchestrator
from tools.email_sender import send_report_email

load_dotenv()

app = FastAPI()

# Request model
class QueryRequest(BaseModel):
    query: str

# API endpoint
@app.post("/generate-report")
def generate_report(request: QueryRequest):
    
    query = request.query

    print(f"Received query: {query}")

    # Run your AI pipeline
    outputs = run_orchestrator(query)

    recipient = os.getenv("DEFAULT_RECIPIENT_EMAIL", "").strip() or None

    if recipient and "@" not in recipient:
        raise HTTPException(status_code=400, detail="Invalid recipient email address")

    email_result = None
    if recipient:
        try:
            email_result = send_report_email(
                recipient_email=recipient,
                report_path=outputs["report_path"],
                query=query,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Email send failed: {exc}") from exc

    return {
        "status": "success",
        "message": "Report generated successfully",
        "report_path": outputs["report_path"],
        "recipient_used": recipient,
        "email": email_result,
    }

# Health check (optional)
@app.get("/")
def home():
    return {"message": "API is running 🚀"}