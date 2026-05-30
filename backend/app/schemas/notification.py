from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.notification import NotificationType, NotificationCategory, NotificationStatus


class NotificationSend(BaseModel):
    batch_id: Optional[str] = None
    student_ids: Optional[List[str]] = None
    schedule_id: Optional[str] = None
    notification_type: NotificationType = NotificationType.BOTH
    category: NotificationCategory = NotificationCategory.CUSTOM
    subject: Optional[str] = None
    message: str


class NotificationLogOut(BaseModel):
    id: str
    batch_id: Optional[str] = None
    schedule_id: Optional[str] = None
    notification_type: NotificationType
    category: NotificationCategory
    status: NotificationStatus
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_whatsapp: Optional[str] = None
    subject: Optional[str] = None
    message_body: Optional[str] = None
    is_bulk: bool
    total_recipients: Optional[str] = None
    success_count: Optional[str] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}
