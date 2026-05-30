from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from datetime import datetime

from app.database import get_db
from app.models.attendance import Attendance, AttendanceStatus
from app.models.student import Student
from app.models.schedule import Schedule
from app.core.dependencies import get_current_user, require_trainer_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/attendance", tags=["attendance"])


@router.get("/{schedule_id}")
async def get_attendance(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    schedule_result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = schedule_result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    students_result = await db.execute(
        select(Student).where(Student.batch_id == schedule.batch_id)
    )
    students = students_result.scalars().all()

    attendance_result = await db.execute(
        select(Attendance).where(Attendance.schedule_id == schedule_id)
    )
    attendances = {str(a.student_id): a for a in attendance_result.scalars().all()}

    return [
        {
            "student_id": str(s.id),
            "name": s.full_name,
            "email": s.email,
            "status": attendances.get(str(s.id), Attendance(status=AttendanceStatus.ABSENT)).status,
            "joined_at": attendances.get(str(s.id), Attendance()).joined_at,
        }
        for s in students
    ]


@router.post("/{schedule_id}/mark")
async def mark_attendance(
    schedule_id: str,
    records: List[dict],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    for record in records:
        student_id = record.get("student_id")
        status = record.get("status", AttendanceStatus.PRESENT)

        existing = await db.execute(
            select(Attendance).where(
                Attendance.schedule_id == schedule_id,
                Attendance.student_id == student_id,
            )
        )
        att = existing.scalar_one_or_none()

        if att:
            att.status = status
            att.joined_at = record.get("joined_at")
        else:
            att = Attendance(
                schedule_id=schedule_id,
                student_id=student_id,
                status=status,
                joined_at=record.get("joined_at"),
                marked_by=f"manual:{current_user.full_name}",
            )
            db.add(att)

    await db.commit()
    return {"message": f"{len(records)} attendance records saved"}


@router.get("/student/{student_id}/summary")
async def student_attendance_summary(
    student_id: str,
    batch_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(func.count()).where(Attendance.student_id == student_id, Attendance.status == AttendanceStatus.PRESENT)
    present = (await db.execute(q)).scalar()

    q2 = select(func.count()).where(Attendance.student_id == student_id)
    total = (await db.execute(q2)).scalar()

    return {
        "student_id": str(student_id),
        "total_classes": total,
        "present": present,
        "absent": total - present,
        "attendance_pct": round((present / total * 100) if total else 0, 1),
    }
