from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from app.services.google_meet import get_oauth_authorization_url, exchange_oauth_code
from app.services.backup import run_backup, list_backups
import os

router = APIRouter(prefix="/api/setup", tags=["setup"])

REDIRECT_URI = "http://localhost:8000/api/setup/google-calendar/callback"


@router.get("/google-calendar")
async def google_calendar_setup():
    """Step 1: Visit this URL to authorize Google Calendar access for Meet link creation."""
    if os.path.exists("credentials/token.json"):
        return HTMLResponse("""
        <html><body style="font-family:sans-serif;background:#1a1a2e;color:#fff;padding:40px;text-align:center">
        <h2 style="color:#22c55e">✅ Google Calendar Already Authorized!</h2>
        <p>Meet links will be auto-created when scheduling classes.</p>
        <p><a href="http://localhost:3000/schedule" style="color:#6366f1">Go to Schedule →</a></p>
        </body></html>
        """)
    auth_url = get_oauth_authorization_url(REDIRECT_URI)
    return RedirectResponse(url=auth_url)


@router.get("/google-calendar/callback")
async def google_calendar_callback(code: str, request: Request):
    """Step 2: Google redirects here after authorization."""
    success = exchange_oauth_code(code, REDIRECT_URI)
    if success:
        return HTMLResponse("""
        <html><body style="font-family:sans-serif;background:#1a1a2e;color:#fff;padding:40px;text-align:center">
        <h2 style="color:#22c55e">✅ Google Calendar Connected!</h2>
        <p style="color:#c0c0d0">Auto Meet link creation is now enabled.</p>
        <p style="color:#c0c0d0">When you schedule a class and check "Auto-create Google Meet", a Meet link will be generated automatically.</p>
        <br>
        <a href="http://localhost:3000/schedule" style="background:#6366f1;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600">
          Go to Schedule →
        </a>
        </body></html>
        """)
    return HTMLResponse("""
    <html><body style="font-family:sans-serif;background:#1a1a2e;color:#fff;padding:40px;text-align:center">
    <h2 style="color:#ef4444">❌ Authorization Failed</h2>
    <p>Please try again: <a href="/api/setup/google-calendar" style="color:#6366f1">Authorize Google Calendar</a></p>
    </body></html>
    """, status_code=400)


@router.get("/status")
async def setup_status():
    """Check which integrations are configured."""
    from app.config import settings
    return {
        "gmail": bool(settings.SMTP_PASSWORD),
        "whatsapp": bool(settings.WHATSAPP_ACCESS_TOKEN and settings.WHATSAPP_PHONE_NUMBER_ID),
        "google_calendar_service_account": os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE),
        "google_calendar_oauth": os.path.exists("credentials/token.json"),
        "meet_auto_creation": os.path.exists("credentials/token.json"),
    }


@router.post("/backup")
async def trigger_backup():
    """Manually trigger a database backup."""
    result = run_backup("manual")
    if result["success"]:
        return {"status": "success", "file": result["file"], "size_kb": result["size_kb"]}
    return {"status": "failed", "error": result.get("error")}


@router.get("/backups")
async def get_backups():
    """List all available backups."""
    backups = list_backups()
    return {"count": len(backups), "backups": backups}
