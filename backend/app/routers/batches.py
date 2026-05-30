from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional


from app.database import get_db
from app.models.batch import Batch
from app.models.student import Student
from app.schemas.batch import BatchCreate, BatchUpdate, BatchOut
from app.core.dependencies import get_current_user, require_trainer_or_admin
from app.models.user import User

router = APIRouter(prefix="/api/batches", tags=["batches"])


@router.get("", response_model=List[BatchOut])
async def list_batches(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = select(Batch)
    if status:
        q = q.where(Batch.status == status)
    result = await db.execute(q.order_by(Batch.created_at.desc()))
    batches = result.scalars().all()

    out = []
    for batch in batches:
        count_result = await db.execute(select(func.count()).where(Student.batch_id == batch.id))
        count = count_result.scalar()
        b = BatchOut.model_validate(batch)
        b.student_count = count
        out.append(b)

    return out


@router.post("", response_model=BatchOut, status_code=201)
async def create_batch(
    batch_in: BatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    batch = Batch(**batch_in.model_dump(exclude_unset=True))
    db.add(batch)
    await db.commit()
    await db.refresh(batch)
    b = BatchOut.model_validate(batch)
    b.student_count = 0
    return b


@router.get("/{batch_id}", response_model=BatchOut)
async def get_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Batch).where(Batch.id == batch_id))
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    count_result = await db.execute(select(func.count()).where(Student.batch_id == batch_id))
    b = BatchOut.model_validate(batch)
    b.student_count = count_result.scalar()
    return b


@router.patch("/{batch_id}", response_model=BatchOut)
async def update_batch(
    batch_id: str,
    batch_in: BatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Batch).where(Batch.id == batch_id))
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    for field, value in batch_in.model_dump(exclude_unset=True).items():
        setattr(batch, field, value)

    await db.commit()
    await db.refresh(batch)

    count_result = await db.execute(select(func.count()).where(Student.batch_id == batch_id))
    b = BatchOut.model_validate(batch)
    b.student_count = count_result.scalar()
    return b


@router.delete("/{batch_id}", status_code=204)
async def delete_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_trainer_or_admin),
):
    result = await db.execute(select(Batch).where(Batch.id == batch_id))
    batch = result.scalar_one_or_none()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
    await db.delete(batch)
    await db.commit()


@router.get("/{batch_id}/students", response_model=List[dict])
async def get_batch_students(
    batch_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(select(Student).where(Student.batch_id == batch_id))
    students = result.scalars().all()
    return [{"id": str(s.id), "name": s.full_name, "email": s.email, "whatsapp": s.whatsapp_number} for s in students]
