from sqlalchemy import Column, String, Boolean, Enum, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class ScheduleStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    RESCHEDULED = "rescheduled"


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
    title = Column(String(255), nullable=True)
    topic = Column(Text, nullable=True)

    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(100), default="Asia/Kolkata")

    google_calendar_event_id = Column(String(255), nullable=True)
    meet_link = Column(Text, nullable=True)

    status = Column(Enum(ScheduleStatus), default=ScheduleStatus.SCHEDULED)
    is_recurring = Column(Boolean, default=False)
    parent_schedule_id = Column(String(36), ForeignKey("schedules.id"), nullable=True)

    original_scheduled_at = Column(DateTime(timezone=True), nullable=True)
    reschedule_reason = Column(Text, nullable=True)
    rescheduled_at = Column(DateTime(timezone=True), nullable=True)

    reminder_sent_24h = Column(Boolean, default=False)
    reminder_sent_1h = Column(Boolean, default=False)
    notifications_sent = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    batch = relationship("Batch", back_populates="schedules")
    attendances = relationship("Attendance", back_populates="schedule", cascade="all, delete-orphan")
    parent = relationship("Schedule", remote_side="Schedule.id", foreign_keys=[parent_schedule_id])
