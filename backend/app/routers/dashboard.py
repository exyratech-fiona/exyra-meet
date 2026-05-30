from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
import pytz

from app.database import get_db
from app.models.batch import Batch, BatchStatus
from app.models.student import Student, StudentStatus
from app.models.schedule import Schedule, ScheduleStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.notification import NotificationLog
from app.core.dependencies import get_current_user
from app.models.user import User
from app.config import settings

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tz = pytz.timezone(settings.DEFAULT_TIMEZONE)
    now = datetime.now(tz)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)
    week_start = today_start - timedelta(days=today_start.weekday())

    # Counts
    total_batches = (await db.execute(select(func.count()).select_from(Batch).where(Batch.status == BatchStatus.ACTIVE))).scalar()
    total_students = (await db.execute(select(func.count()).select_from(Student).where(Student.status == StudentStatus.ACTIVE))).scalar()

    # Today's classes
    todays_classes = (await db.execute(
        select(func.count()).select_from(Schedule).where(
            Schedule.scheduled_at >= today_start,
            Schedule.scheduled_at < today_end,
            Schedule.status.in_([ScheduleStatus.SCHEDULED, ScheduleStatus.ONGOING])
        )
    )).scalar()

    # Upcoming classes (next 7 days)
    upcoming = await db.execute(
        select(Schedule, Batch).join(Batch, Schedule.batch_id == Batch.id)
        .where(
            Schedule.scheduled_at >= now,
            Schedule.scheduled_at <= now + timedelta(days=7),
            Schedule.status == ScheduleStatus.SCHEDULED,
        )
        .order_by(Schedule.scheduled_at.asc())
        .limit(10)
    )
    upcoming_classes = [
        {
            "id": str(row.Schedule.id),
            "batch_name": row.Batch.name,
            "batch_color": row.Batch.color,
            "scheduled_at": row.Schedule.scheduled_at.isoformat(),
            "topic": row.Schedule.topic,
            "meet_link": row.Schedule.meet_link,
            "duration_minutes": row.Schedule.duration_minutes,
        }
        for row in upcoming.fetchall()
    ]

    # Recent notifications
    recent_notifs = await db.execute(
        select(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(5)
    )
    recent_notifications = [
        {
            "id": str(n.id),
            "category": n.category.value,
            "type": n.notification_type.value,
            "status": n.status.value,
            "recipient_name": n.recipient_name,
            "sent_at": n.sent_at.isoformat() if n.sent_at else None,
        }
        for n in recent_notifs.scalars().all()
    ]

    # Attendance rate this week
    week_present = (await db.execute(
        select(func.count()).select_from(Attendance).where(
            Attendance.status == AttendanceStatus.PRESENT,
            Attendance.created_at >= week_start
        )
    )).scalar()

    week_total = (await db.execute(
        select(func.count()).select_from(Attendance).where(Attendance.created_at >= week_start)
    )).scalar()

    attendance_rate = round((week_present / week_total * 100) if week_total else 0, 1)

    # Batch breakdown
    batches_result = await db.execute(
        select(Batch).where(Batch.status == BatchStatus.ACTIVE)
    )
    batches = batches_result.scalars().all()
    batch_breakdown = []
    for batch in batches:
        count = (await db.execute(select(func.count()).where(Student.batch_id == batch.id, Student.status == "active"))).scalar()
        batch_breakdown.append({
            "id": str(batch.id),
            "name": batch.name,
            "course": batch.course,
            "color": batch.color,
            "student_count": count,
        })

    return {
        "total_batches": total_batches,
        "total_students": total_students,
        "todays_classes": todays_classes,
        "upcoming_classes": upcoming_classes,
        "recent_notifications": recent_notifications,
        "attendance_rate": attendance_rate,
        "batch_breakdown": batch_breakdown,
    }
