from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.schedule import Schedule, ScheduleStatus
from app.models.student import Student
from app.models.batch import Batch
from app.services import gmail, whatsapp
import pytz
import structlog

logger = structlog.get_logger()

scheduler = AsyncIOScheduler()


async def send_reminders_for_schedule(schedule_id: str, reminder_type: str):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        schedule = result.scalar_one_or_none()

        if not schedule or schedule.status not in [ScheduleStatus.SCHEDULED, ScheduleStatus.ONGOING]:
            return

        batch_result = await db.execute(select(Batch).where(Batch.id == schedule.batch_id))
        batch = batch_result.scalar_one_or_none()

        students_result = await db.execute(
            select(Student).where(Student.batch_id == schedule.batch_id, Student.status == "active")
        )
        students = students_result.scalars().all()

        tz = pytz.timezone(schedule.timezone or "Asia/Kolkata")
        scheduled_at_str = schedule.scheduled_at.astimezone(tz).strftime("%d %b %Y, %I:%M %p %Z")
        time_until = "1 hour" if reminder_type == "1h" else "24 hours"

        for student in students:
            try:
                if student.email_notifications and student.email:
                    await gmail.send_class_reminder(
                        student_name=student.full_name,
                        email=student.email,
                        batch_name=batch.name if batch else "Your Batch",
                        scheduled_at=scheduled_at_str,
                        topic=schedule.topic or "General Session",
                        duration=schedule.duration_minutes,
                        meet_link=schedule.meet_link or "#",
                        time_until=time_until,
                    )

                if student.whatsapp_notifications and student.whatsapp_number:
                    await whatsapp.send_class_reminder_wa(
                        name=student.full_name,
                        phone=student.whatsapp_number,
                        batch_name=batch.name if batch else "Your Batch",
                        scheduled_at=scheduled_at_str,
                        topic=schedule.topic or "General Session",
                        duration=schedule.duration_minutes,
                        meet_link=schedule.meet_link or "#",
                        time_until=time_until,
                    )
            except Exception as e:
                logger.error("Reminder send failed", student_id=str(student.id), error=str(e))

        # Mark reminder sent
        if reminder_type == "24h":
            schedule.reminder_sent_24h = True
        else:
            schedule.reminder_sent_1h = True

        await db.commit()
        logger.info("Reminders sent", schedule_id=schedule_id, type=reminder_type, count=len(students))


def schedule_reminders(schedule_id: str, scheduled_at: datetime, timezone: str = "Asia/Kolkata"):
    tz = pytz.timezone(timezone)
    if scheduled_at.tzinfo is None:
        scheduled_at = tz.localize(scheduled_at)

    reminder_24h = scheduled_at - timedelta(hours=24)
    reminder_1h = scheduled_at - timedelta(hours=1)
    now = datetime.now(tz)

    if reminder_24h > now:
        scheduler.add_job(
            send_reminders_for_schedule,
            trigger=DateTrigger(run_date=reminder_24h),
            args=[str(schedule_id), "24h"],
            id=f"reminder_24h_{schedule_id}",
            replace_existing=True,
        )

    if reminder_1h > now:
        scheduler.add_job(
            send_reminders_for_schedule,
            trigger=DateTrigger(run_date=reminder_1h),
            args=[str(schedule_id), "1h"],
            id=f"reminder_1h_{schedule_id}",
            replace_existing=True,
        )


def remove_reminders(schedule_id: str):
    for suffix in ["24h", "1h"]:
        job_id = f"reminder_{suffix}_{schedule_id}"
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)


def _daily_backup():
    from app.services.backup import run_backup
    result = run_backup("daily_scheduled")
    if result.get("success"):
        logger.info("Daily backup completed", file=result.get("file"))
    else:
        logger.warning("Daily backup failed", error=result.get("error"))


def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        # Daily backup at 2:00 AM IST
        scheduler.add_job(
            _daily_backup,
            trigger=CronTrigger(hour=2, minute=0, timezone="Asia/Kolkata"),
            id="daily_backup",
            replace_existing=True,
        )
        # Startup backup (runs 10s after start)
        from apscheduler.triggers.date import DateTrigger
        from datetime import datetime, timedelta
        scheduler.add_job(
            _daily_backup,
            trigger=DateTrigger(run_date=datetime.now() + timedelta(seconds=10)),
            id="startup_backup",
            replace_existing=True,
        )
        logger.info("APScheduler started")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped")
