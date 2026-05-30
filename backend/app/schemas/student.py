from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from app.models.student import StudentStatus


class StudentBase(BaseModel):
    full_name: str
    email: EmailStr
    whatsapp_number: Optional[str] = None
    phone_number: Optional[str] = None
    batch_id: Optional[str] = None
    whatsapp_notifications: bool = True
    email_notifications: bool = True


class StudentCreate(StudentBase):
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    fee_amount: Optional[str] = None


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp_number: Optional[str] = None
    phone_number: Optional[str] = None
    batch_id: Optional[str] = None
    status: Optional[StudentStatus] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    whatsapp_notifications: Optional[bool] = None
    email_notifications: Optional[bool] = None
    fee_paid: Optional[bool] = None
    fee_amount: Optional[str] = None


class StudentOut(StudentBase):
    id: str
    status: StudentStatus
    fee_paid: bool
    fee_amount: Optional[str] = None
    avatar_url: Optional[str] = None
    notes: Optional[str] = None
    enrolled_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentBulkCreate(BaseModel):
    students: List[StudentCreate]
    batch_id: Optional[str] = None
