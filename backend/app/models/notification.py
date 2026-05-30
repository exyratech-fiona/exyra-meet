from sqlalchemy import Column, String, Enum, DateTime, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class NotificationType(str, enum.Enum):
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    BOTH = "both"


class NotificationCategory(str, enum.Enum):
    SCHEDULE_REMINDER = "schedule_reminder"
    MEET_LINK = "meet_link"
    RESCHEDULE = "reschedule"
    CANCELLATION = "cancellation"
    WELCOME = "welcome"
    ATTENDANCE = "attendance"
    CUSTOM = "custom"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    PARTIAL = "partial"


class NotificationLog(Base):
    __tablename__ = "notification_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
    schedule_id = Column(String(36), ForeignKey("schedules.id"), nullable=True)
    sent_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    notification_type = Column(Enum(NotificationType), nullable=False)
    category = Column(Enum(NotificationCategory), nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)

    recipient_email = Column(String(255), nullable=True)
    recipient_whatsapp = Column(String(20), nullable=True)
    recipient_name = Column(String(255), nullable=True)

    subject = Column(String(500), nullable=True)
    message_body = Column(Text, nullable=True)
    template_data = Column(JSON, nullable=True)

    is_bulk = Column(Boolean, default=False)
    total_recipients = Column(String(10), nullable=True)
    success_count = Column(String(10), nullable=True)
    error_message = Column(Text, nullable=True)

    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sent_by = relationship("User", back_populates="notification_logs")
