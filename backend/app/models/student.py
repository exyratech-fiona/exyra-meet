from sqlalchemy import Column, String, Boolean, Enum, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class StudentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"


class Student(Base):
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    whatsapp_number = Column(String(20), nullable=True)
    phone_number = Column(String(20), nullable=True)
    avatar_url = Column(Text, nullable=True)

    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=True)
    status = Column(Enum(StudentStatus), default=StudentStatus.ACTIVE)

    date_of_birth = Column(Date, nullable=True)
    address = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    whatsapp_notifications = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)

    fee_paid = Column(Boolean, default=False)
    fee_amount = Column(String(20), nullable=True)

    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    batch = relationship("Batch", back_populates="students")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
