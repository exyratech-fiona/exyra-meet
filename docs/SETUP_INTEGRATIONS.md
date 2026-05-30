# Exyra Technologies — Integration Setup Guide

This guide walks through setting up all three external integrations required for the platform to send automated notifications and create Google Meet links.

---

## 1. Gmail / SMTP Setup

Used for: welcome emails, class reminders, reschedule alerts, Meet link sharing.

### Steps

1. Log in to the Google account you want to send emails from (e.g. `exyratech@gmail.com`)

2. Go to **https://myaccount.google.com/security**

3. Enable **2-Step Verification** (required — App Passwords only work when 2FA is on)

4. Go to **https://myaccount.google.com/apppasswords**

5. In the text box type any name (e.g. `Exyra`) → click **Create**

6. Google shows a 16-character password — copy it immediately (it won't show again)

7. Open `backend/.env` and fill in:

```env
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_SENDER_NAME=Exyra Technologies
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxxxxxxxxxxxxxxxxxx    # 16-char app password, no spaces
```

### Verify

```bash
curl "http://localhost:8000/api/test/gmail?to=your-email@gmail.com"
# Expected: {"status": "success", ...}
```

---

## 2. WhatsApp Cloud API Setup

Used for: class reminders, Meet link sharing, reschedule/cancellation alerts.

### Steps

**A. Create Meta Developer App**

1. Go to **https://developers.facebook.com** → log in with Facebook

2. Click **My Apps** → **Create App**

3. App type → **Other** → Next → **Business** → Next

4. Name: `Exyra Technologies` → email: your business email → **Create App**

5. On the dashboard → find **WhatsApp** → click **Set up**

6. Select business portfolio → click **Continue**

**B. Get Credentials**

7. In left sidebar → **Use cases** → **Customize** (WhatsApp row) → **API Setup**

8. You'll see:
   - **Phone Number ID** → copy this
   - **Temporary Access Token** → click Generate → copy this

9. Open `backend/.env` and fill in:

```env
WHATSAPP_PHONE_NUMBER_ID=1085530781318734
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxxxxxx
```

**C. Add Your Business Phone Number (Production)**

10. In API Setup → scroll to **Step 5: Add a phone number**

11. Click **Add phone number** → enter your business WhatsApp number → verify with OTP

12. Once verified, you can message **any number** without restrictions

> **Note:** Without a verified business number, you can only send to manually approved test numbers. Add your real business number for unrestricted sending.

### Verify

```bash
curl "http://localhost:8000/api/test/whatsapp?to=%2B919444528270"
# Expected: {"status": "success", ...}
```

---

## 3. Google Calendar + Meet Auto-Link Setup

Used for: auto-creating Google Meet links when scheduling classes.

### Steps

**A. Create Google Cloud Project**

1. Go to **https://console.cloud.google.com**

2. Click **Select a project** → **New Project**

3. Name: `Exyra Technologies` → **Create**

**B. Enable Google Calendar API**

4. Click **APIs and services** → **+ Enable APIs and services**

5. Search `Google Calendar API` → click it → click **Enable**

**C. Create Service Account** (for creating calendar events)

6. In left sidebar → **IAM and admin** → **Service accounts** → **+ Create service account**

7. Name: `exyra-calendar` → **Create and continue**

8. Role: **Editor** → **Continue** → **Done**

9. Click the service account → **Keys** tab → **Add Key** → **Create new key** → **JSON** → **Create**

10. A JSON file downloads — rename it to `service_account.json` and place it at:
    ```
    backend/credentials/service_account.json
    ```

11. Copy the `client_email` value from the JSON (looks like `exyra-calendar@project.iam.gserviceaccount.com`)

**D. Share Calendar with Service Account**

12. Go to **https://calendar.google.com** → Settings (gear icon)

13. Click your calendar name → **Shared with** → **+ Add people and groups**

14. Paste the `client_email` → set permission to **Make changes to events** → Save

**E. Set Calendar ID in .env**

15. In Calendar Settings → your calendar → **Integrate calendar** → copy **Calendar ID**

16. Open `backend/.env`:

```env
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service_account.json
GOOGLE_CALENDAR_ID=yourname@gmail.com
```

**F. Enable OAuth for Auto Meet Link Creation** (one-time setup)

17. Go to **https://console.cloud.google.com/apis/credentials** → create **OAuth 2.0 Client ID** (Web application)

18. Add authorized redirect URI: `http://localhost:8000/api/setup/google-calendar/callback`

19. Download the client secret JSON — open it and copy `client_id` and `client_secret` to `.env`:

```env
GOOGLE_CLIENT_ID=xxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxx
```

20. Go to **https://console.cloud.google.com/auth/audience** → add your Gmail as a test user

21. Open this URL in your browser (one-time authorization):
    ```
    http://localhost:8000/api/setup/google-calendar
    ```

22. Log in with your Google account → grant calendar permissions → done!

### Verify

```bash
curl "http://localhost:8000/api/test/google-meet"
# Expected: {"status": "success", "meet_link": "https://meet.google.com/xxx-xxxx-xxx", ...}
```

---

## Check All Integration Status

```bash
curl http://localhost:8000/api/setup/status
```

Expected when everything is working:

```json
{
  "gmail": true,
  "whatsapp": true,
  "google_calendar_service_account": true,
  "google_calendar_oauth": true,
  "meet_auto_creation": true
}
```

---

## Environment Variables Reference

Full `backend/.env` reference:

```env
# App
APP_NAME=Exyra Technologies
SECRET_KEY=your-random-32-char-secret-key
DEBUG=false

# Database
DATABASE_URL=mysql+aiomysql://exyra:password@127.0.0.1:3306/exyra_meet
DATABASE_URL_SYNC=mysql+pymysql://exyra:password@127.0.0.1:3306/exyra_meet

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback

# Google Calendar / Meet
GOOGLE_SERVICE_ACCOUNT_FILE=credentials/service_account.json
GOOGLE_CALENDAR_ID=your-email@gmail.com

# Gmail SMTP
GMAIL_SENDER_EMAIL=your-email@gmail.com
GMAIL_SENDER_NAME=Exyra Technologies
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password

# WhatsApp Cloud API
WHATSAPP_API_URL=https://graph.facebook.com/v19.0
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_VERIFY_TOKEN=exyra_verify_token
```
