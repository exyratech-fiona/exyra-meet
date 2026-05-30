import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, List
from app.config import settings
import structlog

logger = structlog.get_logger()


EMAIL_TEMPLATES = {
    "welcome": {
        "subject": "Welcome to {batch_name} - Exyra Technologies",
        "body": """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: 'Inter', sans-serif; background: #0f0f0f; color: #fff; padding: 32px;">
  <div style="max-width: 600px; margin: 0 auto; background: #1a1a2e; border-radius: 16px; padding: 32px; border: 1px solid #2d2d5a;">
    <div style="text-align: center; margin-bottom: 32px;">
      <h1 style="color: #6366f1; font-size: 28px; margin: 0;">Exyra Technologies</h1>
      <p style="color: #a0a0b0; margin-top: 8px;">Your AI-Powered Training Platform</p>
    </div>
    <h2 style="color: #fff; font-size: 22px;">Welcome, {student_name}! 🎉</h2>
    <p style="color: #c0c0d0; line-height: 1.6;">You've been enrolled in <strong style="color: #6366f1;">{batch_name}</strong>.</p>
    <div style="background: #16213e; border-radius: 12px; padding: 20px; margin: 24px 0; border: 1px solid #2d2d5a;">
      <h3 style="color: #6366f1; margin: 0 0 12px 0;">Batch Details</h3>
      <p style="color: #c0c0d0; margin: 4px 0;"><strong>Course:</strong> {course}</p>
      <p style="color: #c0c0d0; margin: 4px 0;"><strong>Schedule:</strong> {schedule}</p>
      <p style="color: #c0c0d0; margin: 4px 0;"><strong>Trainer:</strong> {trainer}</p>
    </div>
    <p style="color: #c0c0d0;">You'll receive Google Meet links and reminders before each class via email and WhatsApp.</p>
    <div style="text-align: center; margin-top: 32px;">
      <p style="color: #666; font-size: 12px;">© 2024 Exyra Technologies. All rights reserved.</p>
    </div>
  </div>
</body>
</html>
        """,
    },
    "class_reminder": {
        "subject": "Class Reminder: {batch_name} starts in {time_until}",
        "body": """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: 'Inter', sans-serif; background: #0f0f0f; color: #fff; padding: 32px;">
  <div style="max-width: 600px; margin: 0 auto; background: #1a1a2e; border-radius: 16px; padding: 32px; border: 1px solid #2d2d5a;">
    <div style="text-align: center; margin-bottom: 32px;">
      <h1 style="color: #6366f1;">Exyra Technologies</h1>
    </div>
    <h2 style="color: #fff;">⏰ Class Starting Soon, {student_name}!</h2>
    <p style="color: #c0c0d0;">Your <strong style="color: #6366f1;">{batch_name}</strong> class begins in <strong style="color: #22c55e;">{time_until}</strong>.</p>
    <div style="background: #16213e; border-radius: 12px; padding: 20px; margin: 24px 0; border: 1px solid #2d2d5a;">
      <h3 style="color: #6366f1; margin: 0 0 12px 0;">Class Details</h3>
      <p style="color: #c0c0d0; margin: 4px 0;"><strong>Time:</strong> {scheduled_at}</p>
      <p style="color: #c0c0d0; margin: 4px 0;"><strong>Topic:</strong> {topic}</p>
      <p style="color: #c0c0d0; margin: 4px 0;"><strong>Duration:</strong> {duration} minutes</p>
    </div>
    <div style="text-align: center; margin: 24px 0;">
      <a href="{meet_link}" style="background: #6366f1; color: #fff; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 16px; display: inline-block;">
        🎥 Join Google Meet
      </a>
    </div>
    <p style="color: #666; font-size: 12px; text-align: center;">© 2024 Exyra Technologies</p>
  </div>
</body>
</html>
        """,
    },
    "reschedule": {
        "subject": "Class Rescheduled: {batch_name}",
        "body": """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: 'Inter', sans-serif; background: #0f0f0f; color: #fff; padding: 32px;">
  <div style="max-width: 600px; margin: 0 auto; background: #1a1a2e; border-radius: 16px; padding: 32px; border: 1px solid #2d2d5a;">
    <div style="text-align: center; margin-bottom: 32px;">
      <h1 style="color: #6366f1;">Exyra Technologies</h1>
    </div>
    <h2 style="color: #f59e0b;">📅 Class Rescheduled</h2>
    <p style="color: #c0c0d0;">Hi {student_name}, your <strong style="color: #6366f1;">{batch_name}</strong> class has been rescheduled.</p>
    <div style="background: #16213e; border-radius: 12px; padding: 20px; margin: 24px 0; border: 1px solid #2d2d5a;">
      <p style="color: #ef4444; margin: 4px 0;"><strong>Old Time:</strong> <s>{old_time}</s></p>
      <p style="color: #22c55e; margin: 4px 0;"><strong>New Time:</strong> {new_time}</p>
      {reason_block}
    </div>
    <p style="color: #c0c0d0;">A new Google Meet link will be shared before the class.</p>
    <p style="color: #666; font-size: 12px; text-align: center;">© 2024 Exyra Technologies</p>
  </div>
</body>
</html>
        """,
    },
    "cancellation": {
        "subject": "Class Cancelled: {batch_name} - {date}",
        "body": """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: 'Inter', sans-serif; background: #0f0f0f; color: #fff; padding: 32px;">
  <div style="max-width: 600px; margin: 0 auto; background: #1a1a2e; border-radius: 16px; padding: 32px; border: 1px solid #2d2d5a;">
    <div style="text-align: center; margin-bottom: 32px;">
      <h1 style="color: #6366f1;">Exyra Technologies</h1>
    </div>
    <h2 style="color: #ef4444;">❌ Class Cancelled</h2>
    <p style="color: #c0c0d0;">Hi {student_name}, the <strong style="color: #6366f1;">{batch_name}</strong> class scheduled for {date} has been cancelled.</p>
    {reason_block}
    <p style="color: #c0c0d0;">We'll notify you when the next class is scheduled.</p>
    <p style="color: #666; font-size: 12px; text-align: center;">© 2024 Exyra Technologies</p>
  </div>
</body>
</html>
        """,
    },
}


async def send_email(
    to_email: str,
    to_name: str,
    subject: str,
    html_body: str,
) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.GMAIL_SENDER_NAME} <{settings.GMAIL_SENDER_EMAIL}>"
        msg["To"] = f"{to_name} <{to_email}>"

        html_part = MIMEText(html_body, "html")
        msg.attach(html_part)

        smtp_host = settings.SMTP_HOST
        smtp_port = settings.SMTP_PORT
        smtp_user = settings.SMTP_USER or settings.GMAIL_SENDER_EMAIL
        smtp_password = settings.SMTP_PASSWORD

        if not smtp_password:
            logger.warning("SMTP password not set, skipping email", to=to_email)
            return False

        await aiosmtplib.send(
            msg,
            hostname=smtp_host,
            port=smtp_port,
            username=smtp_user,
            password=smtp_password,
            start_tls=True,
        )

        logger.info("Email sent successfully", to=to_email, subject=subject)
        return True

    except Exception as e:
        logger.error("Failed to send email", error=str(e), to=to_email)
        return False


async def send_welcome_email(student_name: str, email: str, batch_name: str, course: str, schedule: str, trainer: str) -> bool:
    template = EMAIL_TEMPLATES["welcome"]
    subject = template["subject"].format(batch_name=batch_name)
    body = template["body"].format(
        student_name=student_name,
        batch_name=batch_name,
        course=course,
        schedule=schedule,
        trainer=trainer,
    )
    return await send_email(email, student_name, subject, body)


async def send_class_reminder(
    student_name: str, email: str, batch_name: str,
    scheduled_at: str, topic: str, duration: int,
    meet_link: str, time_until: str
) -> bool:
    template = EMAIL_TEMPLATES["class_reminder"]
    subject = template["subject"].format(batch_name=batch_name, time_until=time_until)
    body = template["body"].format(
        student_name=student_name, batch_name=batch_name,
        scheduled_at=scheduled_at, topic=topic or "General Session",
        duration=duration, meet_link=meet_link, time_until=time_until,
    )
    return await send_email(email, student_name, subject, body)


async def send_reschedule_email(
    student_name: str, email: str, batch_name: str,
    old_time: str, new_time: str, reason: str = ""
) -> bool:
    template = EMAIL_TEMPLATES["reschedule"]
    reason_block = f'<p style="color: #c0c0d0; margin: 4px 0;"><strong>Reason:</strong> {reason}</p>' if reason else ""
    subject = template["subject"].format(batch_name=batch_name)
    body = template["body"].format(
        student_name=student_name, batch_name=batch_name,
        old_time=old_time, new_time=new_time, reason_block=reason_block,
    )
    return await send_email(email, student_name, subject, body)


async def send_cancellation_email(
    student_name: str, email: str, batch_name: str, date: str, reason: str = ""
) -> bool:
    template = EMAIL_TEMPLATES["cancellation"]
    reason_block = f'<div style="background: #2d1a1a; border-radius: 8px; padding: 12px; margin: 16px 0;"><p style="color: #fca5a5; margin: 0;"><strong>Reason:</strong> {reason}</p></div>' if reason else ""
    subject = template["subject"].format(batch_name=batch_name, date=date)
    body = template["body"].format(
        student_name=student_name, batch_name=batch_name,
        date=date, reason_block=reason_block,
    )
    return await send_email(email, student_name, subject, body)


async def send_bulk_email(recipients: List[dict], template_key: str, template_vars: dict) -> dict:
    success_count = 0
    failed = []
    template = EMAIL_TEMPLATES.get(template_key, EMAIL_TEMPLATES["class_reminder"])

    for recipient in recipients:
        try:
            vars_with_recipient = {**template_vars, "student_name": recipient["name"]}
            subject = template["subject"].format(**vars_with_recipient)
            body = template["body"].format(**vars_with_recipient)
            ok = await send_email(recipient["email"], recipient["name"], subject, body)
            if ok:
                success_count += 1
            else:
                failed.append(recipient["email"])
        except Exception as e:
            failed.append(recipient["email"])
            logger.error("Bulk email failed for recipient", email=recipient["email"], error=str(e))

    return {"success": success_count, "failed": len(failed), "failed_emails": failed}
