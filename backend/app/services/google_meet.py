import os
import json
from datetime import datetime, timedelta
from typing import Optional
import pytz
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config import settings
import structlog

logger = structlog.get_logger()

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

TOKEN_FILE = "credentials/token.json"
CLIENT_SECRETS_FILE = "credentials/client_secret.json"


def _get_oauth_service():
    """Use stored OAuth token (personal Gmail — supports Meet links)."""
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
        if creds and creds.valid:
            return build("calendar", "v3", credentials=creds)
    except Exception as e:
        logger.error("OAuth token load failed", error=str(e))
    return None


def _get_service_account_service():
    """Use service account (creates calendar events, no Meet link on personal Gmail)."""
    try:
        if os.path.exists(settings.GOOGLE_SERVICE_ACCOUNT_FILE):
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            return build("calendar", "v3", credentials=credentials)
        sa_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if sa_info:
            credentials = service_account.Credentials.from_service_account_info(
                json.loads(sa_info), scopes=SCOPES
            )
            return build("calendar", "v3", credentials=credentials)
    except Exception as e:
        logger.error("Service account init failed", error=str(e))
    return None


def get_calendar_service():
    """OAuth token first (supports Meet links), service account as fallback."""
    return _get_oauth_service() or _get_service_account_service()


def get_oauth_authorization_url(redirect_uri: str) -> str:
    """Generate Google OAuth URL for one-time calendar authorization."""
    # Write client secret file if it doesn't exist yet
    if not os.path.exists(CLIENT_SECRETS_FILE) and settings.GOOGLE_CLIENT_ID:
        secret_data = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        }
        os.makedirs("credentials", exist_ok=True)
        with open(CLIENT_SECRETS_FILE, "w") as f:
            json.dump(secret_data, f)

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url


def exchange_oauth_code(code: str, redirect_uri: str) -> bool:
    """Exchange auth code for token and save it."""
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE,
            scopes=SCOPES,
            redirect_uri=redirect_uri,
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        os.makedirs("credentials", exist_ok=True)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        logger.info("Google OAuth token saved successfully")
        return True
    except Exception as e:
        logger.error("OAuth code exchange failed", error=str(e))
        return False


async def create_google_meet_event(
    title: str,
    start_dt: datetime,
    duration_minutes: int,
    timezone: str,
    description: str = "",
    attendee_emails: list = [],
) -> dict:
    service = get_calendar_service()
    if not service:
        logger.warning("Google Calendar service not available")
        return {"meet_link": None, "event_id": None}

    using_oauth = os.path.exists(TOKEN_FILE)

    try:
        tz = pytz.timezone(timezone)
        if start_dt.tzinfo is None:
            start_dt = tz.localize(start_dt)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        event = {
            "summary": title,
            "description": description,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "email", "minutes": 60},
                    {"method": "popup", "minutes": 10},
                ],
            },
        }

        if using_oauth:
            # OAuth user token — can create Meet links and add attendees
            event["conferenceData"] = {
                "createRequest": {
                    "requestId": f"exyra-{start_dt.timestamp()}",
                    "conferenceSolutionKey": {"type": "hangoutsMeet"},
                }
            }
            event["attendees"] = [{"email": e} for e in attendee_emails if e]

        created_event = (
            service.events()
            .insert(
                calendarId=settings.GOOGLE_CALENDAR_ID,
                body=event,
                conferenceDataVersion=1 if using_oauth else 0,
                sendUpdates="all" if using_oauth and attendee_emails else "none",
            )
            .execute()
        )

        meet_link = ""
        if using_oauth:
            meet_link = (
                created_event.get("conferenceData", {})
                .get("entryPoints", [{}])[0]
                .get("uri", "")
            )

        logger.info("Calendar event created", event_id=created_event["id"], meet_link=meet_link, oauth=using_oauth)
        return {"meet_link": meet_link or None, "event_id": created_event["id"]}

    except HttpError as e:
        logger.error("Google Calendar API error", error=str(e))
        return {"meet_link": None, "event_id": None, "error": str(e)}


async def update_google_meet_event(
    event_id: str,
    start_dt: Optional[datetime] = None,
    duration_minutes: Optional[int] = None,
    timezone: Optional[str] = None,
    title: Optional[str] = None,
) -> dict:
    service = get_calendar_service()
    if not service:
        return {"success": False, "error": "Google Calendar service not available"}
    try:
        event = service.events().get(calendarId=settings.GOOGLE_CALENDAR_ID, eventId=event_id).execute()
        if title:
            event["summary"] = title
        if start_dt and timezone:
            tz = pytz.timezone(timezone)
            if start_dt.tzinfo is None:
                start_dt = tz.localize(start_dt)
            end_dt = start_dt + timedelta(minutes=duration_minutes or 60)
            event["start"] = {"dateTime": start_dt.isoformat(), "timeZone": timezone}
            event["end"] = {"dateTime": end_dt.isoformat(), "timeZone": timezone}
        updated = service.events().update(
            calendarId=settings.GOOGLE_CALENDAR_ID, eventId=event_id, body=event, sendUpdates="all"
        ).execute()
        meet_link = (
            updated.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
        )
        return {"success": True, "meet_link": meet_link}
    except HttpError as e:
        logger.error("Failed to update event", error=str(e))
        return {"success": False, "error": str(e)}


async def delete_google_meet_event(event_id: str) -> bool:
    service = get_calendar_service()
    if not service:
        return False
    try:
        service.events().delete(calendarId=settings.GOOGLE_CALENDAR_ID, eventId=event_id).execute()
        return True
    except HttpError as e:
        logger.error("Failed to delete event", error=str(e))
        return False
