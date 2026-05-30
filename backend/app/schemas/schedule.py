from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.schedule import ScheduleStatus


class ScheduleBase(BaseModel):
    batch_id: str
    title: Optional[str] = None
    topic: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 60
    timezone: str = "Asia/Kolkata"


class ScheduleCreate(ScheduleBase):
    meet_link: Optional[str] = None
    is_recurring: bool = False
    auto_create_meet: bool = True


class ScheduleUpdate(BaseModel):
    title: Optional[str] = None
    topic: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    meet_link: Optional[str] = None
    status: Optional[ScheduleStatus] = None
    reschedule_reason: Optional[str] = None


class ScheduleReschedule(BaseModel):
    new_scheduled_at: datetime
    reason: Optional[str] = None
    notify_students: bool = True


class ScheduleOut(ScheduleBase):
    id: str
    status: ScheduleStatus
    meet_link: Optional[str] = None
    google_calendar_event_id: Optional[str] = None
    is_recurring: bool
    original_scheduled_at: Optional[datetime] = None
    reschedule_reason: Optional[str] = None
    reminder_sent_24h: bool
    reminder_sent_1h: bool
    notifications_sent: bool
    created_at: datetime

    model_config = {"from_attributes": True}
