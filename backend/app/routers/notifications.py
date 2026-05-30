from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from datetime import datetime

from app.database import get_db
from app.models.notification import NotificationLog, NotificationType, NotificationStatus
from app.models.student import Student
from app.models.batch import Batch
from app.schemas.notification import NotificationSend, NotificationLogOut
from app.core.dependencies import get_current_user, require_trainer_or_admin
from app.models.user import User
from app.services import gmail, whatsapp

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post("/send")
async def send_notification(
    body: NotificationSend,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    # Resolve recipient list
    recipients = []
    if body.batch_id:
        result = await db.execute(
            select(Student).where(Student.batch_id == body.batch_id, Student.status == "active")
        )
        recipients = result.scalars().all()
    elif body.student_ids:
        result = await db.execute(select(Student).where(Student.id.in_(body.student_ids)))
        recipients = result.scalars().all()

    if not recipients:
        raise HTTPException(status_code=400, detail="No recipients found")

    success_count = 0
    failed_count = 0

    for student in recipients:
        success = True
        if body.notification_type in [NotificationType.EMAIL, NotificationType.BOTH]:
            if student.email and student.email_notifications:
                ok = await gmail.send_email(
                    student.email, student.full_name,
                    body.subject or "Message from Exyra Technologies",
                    f"<div style='font-family:sans-serif;background:#1a1a2e;color:#fff;padding:32px;border-radius:12px;'><h2 style='color:#6366f1;'>Exyra Technologies</h2><p style='color:#c0c0d0;'>{body.message}</p></div>"
                )
                if not ok:
                    success = False

        if body.notification_type in [NotificationType.WHATSAPP, NotificationType.BOTH]:
            if student.whatsapp_number and student.whatsapp_notifications:
                ok = await whatsapp.send_whatsapp_message(student.whatsapp_number, body.message)
                if not ok:
                    success = False

        if success:
            success_count += 1
        else:
            failed_count += 1

        # Log notification
        log = NotificationLog(
            batch_id=body.batch_id,
            schedule_id=body.schedule_id,
            sent_by_id=current_user.id,
            notification_type=body.notification_type,
            category=body.category,
            status=NotificationStatus.SENT if success else NotificationStatus.FAILED,
            recipient_email=student.email,
            recipient_whatsapp=student.whatsapp_number,
            recipient_name=student.full_name,
            subject=body.subject,
            message_body=body.message,
            is_bulk=len(recipients) > 1,
            sent_at=datetime.utcnow() if success else None,
        )
        db.add(log)

    await db.commit()
    return {
        "message": f"Notification sent to {success_count}/{len(recipients)} recipients",
        "success": success_count,
        "failed": failed_count,
    }


@router.get("/logs", response_model=List[NotificationLogOut])
async def get_notification_logs(
    batch_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(NotificationLog).order_by(NotificationLog.created_at.desc()).limit(limit)
    if batch_id:
        q = q.where(NotificationLog.batch_id == batch_id)
    result = await db.execute(q)
    return result.scalars().all()
