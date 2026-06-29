import os
from fastapi import FastAPI
from pydantic import BaseModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = FastAPI()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
ALERT_FROM_EMAIL = os.getenv("ALERT_FROM_EMAIL")
ALERT_TO_EMAIL = os.getenv("ALERT_TO_EMAIL")

class AlertPayload(BaseModel):
    site_name: str
    url: str
    reason: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/alert")
def send_alert(payload: AlertPayload):
    message = Mail(
        from_email=ALERT_FROM_EMAIL,
        to_emails=ALERT_TO_EMAIL,
        subject=f"🚨 {payload.site_name} is down",
        html_content=f"""
            <h1>Site Down Alert</h1>
            <p><strong>Site:</strong> {payload.site_name}</p>
            <p><strong>URL:</strong> {payload.url}</p>
            <p><strong>Reason:</strong> {payload.reason}</p>
        """
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        return {"status": "alert sent"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}