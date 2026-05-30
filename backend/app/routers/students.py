from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List, Optional


from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut, StudentBulkCreate
from app.core.dependencies import get_current_user, require_trainer_or_admin
from app.services.backup import run_backup
import asyncio
from app.models.user import User
from app.models.batch import Batch
from app.services import gmail, whatsapp

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("", response_model=List[StudentOut])
async def list_students(
    batch_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Student)
    if batch_id:
        q = q.where(Student.batch_id == batch_id)
    if status:
        q = q.where(Student.status == status)
    if search:
        q = q.where(
            or_(
                Student.full_name.ilike(f"%{search}%"),
                Student.email.ilike(f"%{search}%"),
            )
        )
    result = await db.execute(q.order_by(Student.enrolled_at.desc()))
    return result.scalars().all()


@router.post("", response_model=StudentOut, status_code=201)
async def create_student(
    student_in: StudentCreate,
    send_welcome: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    student = Student(**student_in.model_dump(exclude_unset=True))
    db.add(student)
    await db.commit()
    await db.refresh(student)

    if send_welcome and student.batch_id:
        batch_result = await db.execute(select(Batch).where(Batch.id == student.batch_id))
        batch = batch_result.scalar_one_or_none()
        if batch:
            schedule_str = f"{batch.recurrence_type.value.title()} at {batch.default_start_time or 'TBD'}"
            if student.email and student.email_notifications:
                await gmail.send_welcome_email(
                    student.full_name, student.email,
                    batch.name, batch.course, schedule_str, "Your Trainer"
                )
            if student.whatsapp_number and student.whatsapp_notifications:
                await whatsapp.send_welcome_wa(
                    student.full_name, student.whatsapp_number,
                    batch.name, batch.course, schedule_str
                )

    # Auto-backup after new student added
    asyncio.get_event_loop().run_in_executor(None, run_backup, f"student_added:{student.full_name}")

    return student


@router.post("/bulk", status_code=201)
async def bulk_create_students(
    body: StudentBulkCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    created = []
    for s in body.students:
        data = s.model_dump(exclude_unset=True)
        if body.batch_id and not data.get("batch_id"):
            data["batch_id"] = body.batch_id
        student = Student(**data)
        db.add(student)
        created.append(student)

    await db.commit()
    return {"created": len(created), "message": f"{len(created)} students added successfully"}


@router.get("/{student_id}", response_model=StudentOut)
async def get_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: str,
    student_in: StudentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    for field, value in student_in.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    await db.commit()
    await db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=204)
async def delete_student(
    student_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await db.delete(student)
    await db.commit()
