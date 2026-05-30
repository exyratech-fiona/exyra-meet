from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional

from datetime import datetime, timedelta
import pytz

from app.database import get_db
from app.models.schedule import Schedule, ScheduleStatus
from app.models.student import Student
from app.models.batch import Batch
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut, ScheduleReschedule
from app.core.dependencies import get_current_user, require_trainer_or_admin
from app.models.user import User
from app.services import google_meet, gmail, whatsapp
from app.services.scheduler import schedule_reminders, remove_reminders

router = APIRouter(prefix="/api/schedules", tags=["schedules"])


@router.get("", response_model=List[ScheduleOut])
async def list_schedules(
    batch_id: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Schedule)
    if batch_id:
        q = q.where(Schedule.batch_id == batch_id)
    if from_date:
        q = q.where(Schedule.scheduled_at >= from_date)
    if to_date:
        q = q.where(Schedule.scheduled_at <= to_date)
    if status:
        q = q.where(Schedule.status == status)

    result = await db.execute(q.order_by(Schedule.scheduled_at.asc()))
    return result.scalars().all()


@router.post("", response_model=ScheduleOut, status_code=201)
async def create_schedule(
    schedule_in: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    batch_result = await db.execute(select(Batch).where(Batch.id == schedule_in.batch_id))
    batch = batch_result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    data = schedule_in.model_dump(exclude={"auto_create_meet"})
    schedule = Schedule(**data)
    db.add(schedule)
    await db.flush()

    # Auto-create Google Meet
    if schedule_in.auto_create_meet and not schedule_in.meet_link:
        students_result = await db.execute(
            select(Student.email).where(Student.batch_id == schedule_in.batch_id)
        )
        emails = [r[0] for r in students_result.fetchall() if r[0]]

        meet_data = await google_meet.create_google_meet_event(
            title=f"{batch.name} - {schedule_in.title or 'Class'}",
            start_dt=schedule_in.scheduled_at,
            duration_minutes=schedule_in.duration_minutes,
            timezone=schedule_in.timezone,
            description=schedule_in.topic or "",
            attendee_emails=emails,
        )
        schedule.meet_link = meet_data.get("meet_link")
        schedule.google_calendar_event_id = meet_data.get("event_id")

    await db.commit()
    await db.refresh(schedule)

    # Schedule APScheduler reminders
    schedule_reminders(schedule.id, schedule.scheduled_at, schedule.timezone)

    return schedule


@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: str,
    schedule_in: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    for field, value in schedule_in.model_dump(exclude_unset=True).items():
        setattr(schedule, field, value)

    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.post("/{schedule_id}/reschedule", response_model=ScheduleOut)
async def reschedule(
    schedule_id: str,
    body: ScheduleReschedule,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    batch_result = await db.execute(select(Batch).where(Batch.id == schedule.batch_id))
    batch = batch_result.scalar_one_or_none()

    tz = pytz.timezone(schedule.timezone or "Asia/Kolkata")
    old_time_str = schedule.scheduled_at.astimezone(tz).strftime("%d %b %Y, %I:%M %p %Z")
    new_time_str = body.new_scheduled_at.astimezone(tz).strftime("%d %b %Y, %I:%M %p %Z") if body.new_scheduled_at.tzinfo else body.new_scheduled_at.strftime("%d %b %Y, %I:%M %p")

    schedule.original_scheduled_at = schedule.original_scheduled_at or schedule.scheduled_at
    schedule.scheduled_at = body.new_scheduled_at
    schedule.reschedule_reason = body.reason
    schedule.rescheduled_at = datetime.utcnow()
    schedule.status = ScheduleStatus.RESCHEDULED
    schedule.reminder_sent_24h = False
    schedule.reminder_sent_1h = False

    # Update Google Calendar event
    if schedule.google_calendar_event_id:
        await google_meet.update_google_meet_event(
            schedule.google_calendar_event_id,
            start_dt=body.new_scheduled_at,
            duration_minutes=schedule.duration_minutes,
            timezone=schedule.timezone,
        )

    await db.commit()

    # Re-schedule reminders
    remove_reminders(schedule_id)
    schedule_reminders(schedule_id, body.new_scheduled_at, schedule.timezone)

    if body.notify_students:
        students_result = await db.execute(
            select(Student).where(Student.batch_id == schedule.batch_id, Student.status == "active")
        )
        students = students_result.scalars().all()

        for student in students:
            if student.email and student.email_notifications:
                await gmail.send_reschedule_email(
                    student.full_name, student.email,
                    batch.name if batch else "Batch",
                    old_time_str, new_time_str, body.reason or ""
                )
            if student.whatsapp_number and student.whatsapp_notifications:
                await whatsapp.send_reschedule_wa(
                    student.full_name, student.whatsapp_number,
                    batch.name if batch else "Batch",
                    old_time_str, new_time_str, body.reason or ""
                )

    await db.refresh(schedule)
    return schedule


@router.post("/{schedule_id}/cancel", response_model=ScheduleOut)
async def cancel_schedule(
    schedule_id: str,
    reason: Optional[str] = Query(None),
    notify_students: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    schedule.status = ScheduleStatus.CANCELLED
    remove_reminders(schedule_id)

    batch_result = await db.execute(select(Batch).where(Batch.id == schedule.batch_id))
    batch = batch_result.scalar_one_or_none()

    if notify_students:
        students_result = await db.execute(
            select(Student).where(Student.batch_id == schedule.batch_id, Student.status == "active")
        )
        students = students_result.scalars().all()
        tz = pytz.timezone(schedule.timezone or "Asia/Kolkata")
        date_str = schedule.scheduled_at.astimezone(tz).strftime("%d %b %Y, %I:%M %p %Z")

        for student in students:
            if student.email and student.email_notifications:
                await gmail.send_cancellation_email(
                    student.full_name, student.email,
                    batch.name if batch else "Batch", date_str, reason or ""
                )
            if student.whatsapp_number and student.whatsapp_notifications:
                await whatsapp.send_cancellation_wa(
                    student.full_name, student.whatsapp_number,
                    batch.name if batch else "Batch", date_str, reason or ""
                )

    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.post("/{schedule_id}/send-link")
async def send_meet_link(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    if not schedule.meet_link:
        raise HTTPException(status_code=400, detail="No Meet link available")

    batch_result = await db.execute(select(Batch).where(Batch.id == schedule.batch_id))
    batch = batch_result.scalar_one_or_none()

    students_result = await db.execute(
        select(Student).where(Student.batch_id == schedule.batch_id, Student.status == "active")
    )
    students = students_result.scalars().all()

    tz = pytz.timezone(schedule.timezone or "Asia/Kolkata")
    scheduled_at_str = schedule.scheduled_at.astimezone(tz).strftime("%d %b %Y, %I:%M %p %Z")

    sent = 0
    for student in students:
        if student.email and student.email_notifications:
            ok = await gmail.send_class_reminder(
                student.full_name, student.email,
                batch.name if batch else "Batch",
                scheduled_at_str, schedule.topic or "General Session",
                schedule.duration_minutes, schedule.meet_link, "soon"
            )
            if ok:
                sent += 1
        if student.whatsapp_number and student.whatsapp_notifications:
            await whatsapp.send_meet_link_wa(
                student.full_name, student.whatsapp_number,
                batch.name if batch else "Batch",
                schedule.meet_link, scheduled_at_str
            )

    schedule.notifications_sent = True
    await db.commit()

    return {"message": f"Meet link sent to {sent} students", "sent_count": sent}
