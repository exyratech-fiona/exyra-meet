from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.config import settings
from app.database import init_db
from app.services.scheduler import start_scheduler, stop_scheduler
from app.routers import auth, batches, students, schedules, notifications, attendance, dashboard
from app.routers import test_integrations
from app.routers import setup

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Exyra Technologies API", version=settings.APP_VERSION)
    # Retry DB init up to 5 times (MySQL may still be booting)
    for attempt in range(5):
        try:
            await init_db()
            logger.info("Database connected and tables ready")
            break
        except Exception as e:
            if attempt == 4:
                logger.error("Database connection failed after 5 attempts", error=str(e))
            else:
                import asyncio
                logger.warning(f"DB not ready (attempt {attempt+1}/5), retrying in 3s...")
                await asyncio.sleep(3)
    start_scheduler()
    yield
    stop_scheduler()
    logger.info("Shutting down API")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Batch management platform for Exyra Technologies",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(batches.router)
app.include_router(students.router)
app.include_router(schedules.router)
app.include_router(notifications.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)
app.include_router(test_integrations.router)
app.include_router(setup.router)


@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION, "service": settings.APP_NAME}
