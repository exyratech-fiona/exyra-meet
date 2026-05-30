import httpx
from typing import Optional, List
from app.config import settings
import structlog

logger = structlog.get_logger()

WA_API_URL = f"{settings.WHATSAPP_API_URL}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"

WA_TEMPLATES = {
    "class_reminder": """
🎓 *Exyra Technologies*

Hey {name}! 👋

📚 *{batch_name}* class is starting in *{time_until}*!

📅 *Time:* {scheduled_at}
📖 *Topic:* {topic}
⏱️ *Duration:* {duration} minutes

🎥 *Join Now:*
{meet_link}

See you there! 🚀
""",
    "meet_link": """
🎓 *Exyra Technologies*

Hi {name}! 🙌

Here's your Google Meet link for *{batch_name}*:

🎥 *Meet Link:*
{meet_link}

📅 *Scheduled:* {scheduled_at}

Click the link to join. Good luck! 💪
""",
    "reschedule": """
🎓 *Exyra Technologies*

Hi {name},

Your *{batch_name}* class has been *rescheduled* 📅

❌ *Old Time:* {old_time}
✅ *New Time:* {new_time}
{reason_line}
You'll receive the updated Meet link before the class.

Apologies for any inconvenience! 🙏
""",
    "cancellation": """
🎓 *Exyra Technologies*

Hi {name},

We regret to inform you that the *{batch_name}* class on *{date}* has been *cancelled* ❌
{reason_line}
We'll notify you when the next class is scheduled.

Thank you for your understanding 🙏
""",
    "welcome": """
🎓 *Welcome to Exyra Technologies!*

Hi {name}! 🎉

You've been successfully enrolled in *{batch_name}*!

📚 *Course:* {course}
📅 *Schedule:* {schedule}

You'll receive class reminders, Google Meet links, and updates here on WhatsApp.

Welcome aboard! 🚀✨
""",
    "custom": """{message}""",
}


async def send_whatsapp_message(phone: str, message: str) -> bool:
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp credentials not configured, skipping", phone=phone)
        return False

    # Normalize phone number — strip spaces/dashes, ensure country code
    phone = phone.strip().replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "+91" + phone[1:]   # 09876... → +919876...
    elif not phone.startswith("+"):
        phone = "+91" + phone       # 9876... → +919876...

    phone = phone.lstrip("+")

    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {"preview_url": True, "body": message},
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(WA_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            logger.info("WhatsApp message sent", phone=phone)
            return True
    except httpx.HTTPStatusError as e:
        logger.error("WhatsApp API HTTP error", status=e.response.status_code, error=e.response.text, phone=phone)
        return False
    except Exception as e:
        logger.error("WhatsApp send failed", error=str(e), phone=phone)
        return False


async def send_class_reminder_wa(
    name: str, phone: str, batch_name: str,
    scheduled_at: str, topic: str, duration: int,
    meet_link: str, time_until: str
) -> bool:
    msg = WA_TEMPLATES["class_reminder"].format(
        name=name, batch_name=batch_name, time_until=time_until,
        scheduled_at=scheduled_at, topic=topic or "General Session",
        duration=duration, meet_link=meet_link,
    )
    return await send_whatsapp_message(phone, msg)


async def send_meet_link_wa(name: str, phone: str, batch_name: str, meet_link: str, scheduled_at: str) -> bool:
    msg = WA_TEMPLATES["meet_link"].format(
        name=name, batch_name=batch_name,
        meet_link=meet_link, scheduled_at=scheduled_at,
    )
    return await send_whatsapp_message(phone, msg)


async def send_reschedule_wa(
    name: str, phone: str, batch_name: str, old_time: str, new_time: str, reason: str = ""
) -> bool:
    reason_line = f"\n📝 *Reason:* {reason}" if reason else ""
    msg = WA_TEMPLATES["reschedule"].format(
        name=name, batch_name=batch_name,
        old_time=old_time, new_time=new_time, reason_line=reason_line,
    )
    return await send_whatsapp_message(phone, msg)


async def send_cancellation_wa(name: str, phone: str, batch_name: str, date: str, reason: str = "") -> bool:
    reason_line = f"\n📝 *Reason:* {reason}" if reason else ""
    msg = WA_TEMPLATES["cancellation"].format(
        name=name, batch_name=batch_name, date=date, reason_line=reason_line,
    )
    return await send_whatsapp_message(phone, msg)


async def send_welcome_wa(name: str, phone: str, batch_name: str, course: str, schedule: str) -> bool:
    msg = WA_TEMPLATES["welcome"].format(
        name=name, batch_name=batch_name, course=course, schedule=schedule,
    )
    return await send_whatsapp_message(phone, msg)


async def send_bulk_whatsapp(recipients: List[dict], template_key: str, template_vars: dict) -> dict:
    success_count = 0
    failed = []

    for recipient in recipients:
        if not recipient.get("whatsapp"):
            continue
        try:
            vars_with_recipient = {**template_vars, "name": recipient["name"]}
            msg = WA_TEMPLATES.get(template_key, WA_TEMPLATES["custom"]).format(**vars_with_recipient)
            ok = await send_whatsapp_message(recipient["whatsapp"], msg)
            if ok:
                success_count += 1
            else:
                failed.append(recipient["whatsapp"])
        except Exception as e:
            failed.append(recipient.get("whatsapp", "unknown"))
            logger.error("Bulk WA failed", phone=recipient.get("whatsapp"), error=str(e))

    return {"success": success_count, "failed": len(failed)}
