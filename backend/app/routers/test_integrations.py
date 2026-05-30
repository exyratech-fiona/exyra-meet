from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
import pytz
from app.services import gmail, whatsapp, google_meet
from app.config import settings

router = APIRouter(prefix="/api/test", tags=["test-integrations"])


@router.get("/gmail")
async def test_gmail(to: str = Query(..., description="Recipient email address")):
    """Send a test email to verify Gmail/SMTP is configured correctly."""
    html = """
    <div style="font-family:Inter,sans-serif;background:#1a1a2e;color:#fff;padding:32px;border-radius:12px;max-width:500px">
      <h2 style="color:#6366f1;">✅ Gmail Integration Working!</h2>
      <p style="color:#c0c0d0;">This is a test email from <strong>Exyra Technologies</strong>.</p>
      <p style="color:#c0c0d0;">Your Gmail SMTP is configured correctly and ready to send:</p>
      <ul style="color:#a0a0b0;">
        <li>Class reminders</li>
        <li>Google Meet links</li>
        <li>Reschedule notifications</li>
        <li>Welcome emails</li>
      </ul>
      <p style="color:#666;font-size:12px;margin-top:24px;">Sent from Exyra Technologies Platform</p>
    </div>
    """
    ok = await gmail.send_email(to, to.split("@")[0], "✅ Exyra Gmail Test — Working!", html)
    if ok:
        return {"status": "success", "message": f"Test email sent to {to}", "from": settings.GMAIL_SENDER_EMAIL}
    raise HTTPException(status_code=500, detail="Failed to send email. Check SMTP credentials in .env")


@router.get("/whatsapp")
async def test_whatsapp(to: str = Query(..., description="WhatsApp number with country code e.g. +919876543210")):
    """Send a test WhatsApp message to verify the Cloud API is configured correctly."""
    message = (
        "✅ *Exyra Technologies*\n\n"
        "WhatsApp integration is working! 🎉\n\n"
        "You will now receive:\n"
        "📅 Class reminders\n"
        "🎥 Google Meet links\n"
        "🔔 Reschedule alerts\n\n"
        "_Sent from Exyra Technologies Platform_"
    )
    ok = await whatsapp.send_whatsapp_message(to, message)
    if ok:
        return {"status": "success", "message": f"Test WhatsApp sent to {to}"}
    raise HTTPException(
        status_code=500,
        detail="Failed to send WhatsApp. Check WHATSAPP_PHONE_NUMBER_ID and WHATSAPP_ACCESS_TOKEN in .env"
    )


@router.get("/google-meet")
async def test_google_meet():
    """Create a test Google Calendar event with a Meet link."""
    tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    start = datetime.now(tz) + timedelta(hours=1)

    result = await google_meet.create_google_meet_event(
        title="Exyra Test Class — Integration Check",
        start_dt=start,
        duration_minutes=30,
        timezone=settings.DEFAULT_TIMEZONE,
        description="This is a test event created by Exyra Technologies platform to verify Google Calendar integration.",
        attendee_emails=[settings.GMAIL_SENDER_EMAIL],
    )

    if result.get("event_id"):
        return {
            "status": "success",
            "event_id": result["event_id"],
            "meet_link": result.get("meet_link") or None,
            "message": "Calendar event created! Check your Google Calendar (exyratech@gmail.com)."
            + (" Meet link auto-generated." if result.get("meet_link") else " No Meet link — personal Gmail limitation. Paste Meet link manually in the Schedule page."),
        }
    raise HTTPException(
        status_code=500,
        detail="Failed to create calendar event. Check service_account.json and Google Calendar API is enabled."
    )


@router.get("/all")
async def test_all(
    email: str = Query(..., description="Email to test Gmail"),
    phone: str = Query(..., description="WhatsApp number e.g. +919876543210"),
):
    """Run all three integration tests at once."""
    results = {}

    # Gmail
    try:
        html = "<div style='font-family:sans-serif;padding:20px'><h2>✅ Exyra Gmail Test</h2><p>All integrations running!</p></div>"
        results["gmail"] = "success" if await gmail.send_email(email, "Test", "Exyra Integration Test", html) else "failed"
    except Exception as e:
        results["gmail"] = f"error: {str(e)}"

    # WhatsApp
    try:
        msg = "✅ *Exyra* — All integrations test running! WhatsApp is working."
        results["whatsapp"] = "success" if await whatsapp.send_whatsapp_message(phone, msg) else "failed"
    except Exception as e:
        results["whatsapp"] = f"error: {str(e)}"

    # Google Meet
    try:
        tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
        r = await google_meet.create_google_meet_event(
            title="Exyra Integration Test",
            start_dt=datetime.now(tz) + timedelta(hours=1),
            duration_minutes=30,
            timezone=settings.DEFAULT_TIMEZONE,
        )
        results["google_meet"] = r.get("meet_link") or "failed — check service account"
    except Exception as e:
        results["google_meet"] = f"error: {str(e)}"

    return results
