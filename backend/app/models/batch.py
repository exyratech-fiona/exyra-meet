from sqlalchemy import Column, String, Boolean, Enum, DateTime, Text, Time, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class BatchStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecurrenceType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class Batch(Base):
    __tablename__ = "batches"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    course = Column(String(255), nullable=False)
    trainer_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    status = Column(Enum(BatchStatus), default=BatchStatus.ACTIVE)

    # Timing
    timezone = Column(String(100), default="Asia/Kolkata")
    default_start_time = Column(Time, nullable=True)
    default_duration_minutes = Column(Integer, default=60)
    recurrence_type = Column(Enum(RecurrenceType), default=RecurrenceType.WEEKLY)
    recurrence_days = Column(String(50), nullable=True)  # comma-sep: "0,2,4" = Mon,Wed,Fri

    # Google Meet
    google_calendar_event_id = Column(String(255), nullable=True)
    google_meet_link = Column(Text, nullable=True)
    custom_meet_link = Column(Text, nullable=True)

    # Metadata
    color = Column(String(7), default="#6366f1")
    max_students = Column(Integer, default=30)
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    trainer = relationship("User", back_populates="trainer_batches", foreign_keys=[trainer_id])
    students = relationship("Student", back_populates="batch")
    schedules = relationship("Schedule", back_populates="batch", cascade="all, delete-orphan")
