from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, time
from app.models.batch import BatchStatus, RecurrenceType


class BatchBase(BaseModel):
    name: str
    description: Optional[str] = None
    course: str
    timezone: str = "Asia/Kolkata"
    default_start_time: Optional[time] = None
    default_duration_minutes: int = 60
    recurrence_type: RecurrenceType = RecurrenceType.WEEKLY
    recurrence_days: Optional[str] = None  # comma-sep e.g. "0,2,4"
    color: str = "#6366f1"
    max_students: int = 30


class BatchCreate(BatchBase):
    trainer_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BatchUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    course: Optional[str] = None
    trainer_id: Optional[str] = None
    status: Optional[BatchStatus] = None
    timezone: Optional[str] = None
    default_start_time: Optional[time] = None
    default_duration_minutes: Optional[int] = None
    recurrence_type: Optional[RecurrenceType] = None
    recurrence_days: Optional[str] = None
    color: Optional[str] = None
    max_students: Optional[int] = None
    custom_meet_link: Optional[str] = None


class BatchOut(BatchBase):
    id: str
    status: BatchStatus
    trainer_id: Optional[str] = None
    google_meet_link: Optional[str] = None
    custom_meet_link: Optional[str] = None
    student_count: Optional[int] = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class BatchSummary(BaseModel):
    id: str
    name: str
    course: str
    color: str
    status: BatchStatus
    student_count: int = 0

    model_config = {"from_attributes": True}
