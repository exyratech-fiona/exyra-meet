# Exyra Technologies — Batch Management Platform

A premium automation platform for managing online training batches, student communication, Google Meet scheduling, WhatsApp notifications, and Gmail alerts.

---

## Quick Start

```bash
# 1. Clone / navigate to project
cd /path/to/Meet

# 2. Start all services (runs in background)
./start.sh

# 3. Open the app
open http://localhost:3000
```

Default login: `admin@exyra.tech` / `admin123`

---

## What's Running

| Service    | URL                              | Description                    |
|------------|----------------------------------|--------------------------------|
| Frontend   | http://localhost:3000            | Web app (Next.js)              |
| Backend    | http://localhost:8000            | REST API (FastAPI)             |
| API Docs   | http://localhost:8000/api/docs   | Swagger interactive docs       |
| MySQL      | 127.0.0.1:3306 / exyra_meet     | Database                       |

---

## Stop All Services

```bash
./stop.sh
```

---

## Features

- **Student Management** — Add/edit/delete students, assign to batches, track fees
- **Batch Management** — Create batches (AI, DevOps, School, etc.), set timings and recurrence
- **Google Meet Auto-creation** — Automatically generates Meet links when scheduling classes
- **WhatsApp Automation** — Sends class reminders, Meet links, reschedule/cancellation alerts
- **Gmail Automation** — Sends HTML emails for all class events
- **Attendance Tracking** — Mark present/absent/late per class session
- **Notification Center** — Send bulk or targeted messages manually
- **Admin Dashboard** — Upcoming classes, batch stats, attendance rate, notification log

---

## First-Time Setup

### Prerequisites

- Docker Desktop (for MySQL)
- Python 3.12
- Node.js 20+

### 1. Configure Environment

Copy the example file and fill in your credentials:

```bash
cp .env.example backend/.env
```

Edit `backend/.env` with your values. See [`docs/SETUP_INTEGRATIONS.md`](docs/SETUP_INTEGRATIONS.md) for detailed instructions on each integration.

### 2. Start the Platform

```bash
./start.sh
```

The script automatically:
- Starts MySQL via Docker
- Creates a Python 3.12 virtual environment
- Installs all backend dependencies
- Creates all database tables
- Starts the FastAPI backend on port 8000
- Installs frontend npm packages
- Starts the Next.js frontend on port 3000

### 3. Set Up Integrations (one-time)

After the platform is running, set up the three integrations:

| Integration    | Setup Guide                                    |
|----------------|------------------------------------------------|
| Gmail SMTP     | [docs/SETUP_INTEGRATIONS.md](docs/SETUP_INTEGRATIONS.md#1-gmail--smtp-setup) |
| WhatsApp API   | [docs/SETUP_INTEGRATIONS.md](docs/SETUP_INTEGRATIONS.md#2-whatsapp-cloud-api-setup) |
| Google Meet    | [docs/SETUP_INTEGRATIONS.md](docs/SETUP_INTEGRATIONS.md#3-google-calendar--meet-auto-link-setup) |

Then authorize Google Calendar (one-time, takes 30 seconds):

```
http://localhost:8000/api/setup/google-calendar
```

Check all integrations are working:

```
http://localhost:8000/api/setup/status
```

---

## Tech Stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Frontend   | Next.js 14, Tailwind CSS, Framer Motion |
| Backend    | FastAPI, SQLAlchemy (async), APScheduler |
| Database   | MySQL 8.0 (Docker)                      |
| Auth       | JWT + Google OAuth                      |
| WhatsApp   | Meta WhatsApp Cloud API                 |
| Email      | Gmail SMTP (App Password)               |
| Calendar   | Google Calendar API + OAuth             |

---

## Project Structure

```
Meet/
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── routers/          # API endpoints
│   │   └── services/         # WhatsApp, Gmail, Google Meet
│   ├── credentials/          # Google service account + OAuth token (gitignored)
│   ├── .env                  # Environment variables (gitignored)
│   └── requirements.txt
├── frontend/                 # Next.js frontend
│   ├── app/                  # Pages (dashboard, batches, students, schedule...)
│   ├── components/           # Reusable UI components
│   └── lib/                  # API client, utilities, store
├── docs/
│   └── SETUP_INTEGRATIONS.md # Integration setup guide
├── docker-compose.yml        # Full Docker deployment
├── start.sh                  # Start all services in background
├── stop.sh                   # Stop all services
└── README.md
```

---

## Manual Start (without start.sh)

```bash
# Terminal 1 — MySQL
docker start exyra_mysql

# Terminal 2 — Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3 — Frontend
cd frontend
npm run dev -- --port 3000
```

---

## Logs

```bash
tail -f /tmp/exyra_backend.log    # Backend logs
tail -f /tmp/exyra_frontend.log   # Frontend logs
```

---

## Docker Compose (Production)

To run everything in Docker containers:

```bash
docker compose up --build -d
```

Access at http://localhost:3000 — MySQL, backend, and frontend all containerized.

---

## Support

For integration issues, check [`docs/SETUP_INTEGRATIONS.md`](docs/SETUP_INTEGRATIONS.md).

Built for Exyra Technologies — AI & DevOps Training Institute.
