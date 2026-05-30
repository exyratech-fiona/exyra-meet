from sqlalchemy import Column, String, Boolean, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    TRAINER = "trainer"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.TRAINER, nullable=False)
    google_id = Column(String(255), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    trainer_batches = relationship("Batch", back_populates="trainer", foreign_keys="Batch.trainer_id")
    notification_logs = relationship("NotificationLog", back_populates="sent_by")
