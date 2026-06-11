"""Wrong-answer book service — CRUD + AI similar-question generation."""

import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.wrong_answer import WrongAnswer
from ..models.user import User


async def list_wrong_answers(
    db: AsyncSession,
    user_id: uuid.UUID,
    subject: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """List user's wrong answers, optionally filtered by subject."""
    query = select(WrongAnswer).where(WrongAnswer.user_id == user_id)
    count_q = select(func.count(WrongAnswer.id)).where(WrongAnswer.user_id == user_id)

    if subject:
        query = query.where(WrongAnswer.subject == subject)
        count_q = count_q.where(WrongAnswer.subject == subject)

    query = query.order_by(WrongAnswer.created_at.desc()).offset((page - 1) * page_size).limit(page_size)

    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    result = await db.execute(query)
    items = list(result.scalars().all())

    return {"items": items, "total": total, "page": page, "page_size": page_size}


async def get_wrong_answer(db: AsyncSession, user_id: uuid.UUID, wa_id: uuid.UUID) -> WrongAnswer | None:
    """Get a single wrong answer, scoped to the user."""
    result = await db.execute(
        select(WrongAnswer).where(WrongAnswer.id == wa_id, WrongAnswer.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_wrong_answer(
    db: AsyncSession,
    user_id: uuid.UUID,
    subject: str | None,
    question: str,
    answer: str | None = None,
    correct_answer: str | None = None,
    tags: list[str] | None = None,
) -> WrongAnswer:
    """Add a new wrong answer entry."""
    wa = WrongAnswer(
        user_id=user_id,
        subject=subject,
        question=question,
        answer=answer,
        correct_answer=correct_answer,
        tags=tags or [],
    )
    db.add(wa)
    await db.commit()
    await db.refresh(wa)
    return wa


async def update_wrong_answer(
    db: AsyncSession,
    user_id: uuid.UUID,
    wa_id: uuid.UUID,
    **kwargs,
) -> WrongAnswer | None:
    """Update a wrong answer entry. Only modifies provided fields."""
    wa = await get_wrong_answer(db, user_id, wa_id)
    if wa is None:
        return None

    for field, value in kwargs.items():
        if hasattr(wa, field) and value is not None:
            setattr(wa, field, value)

    await db.commit()
    await db.refresh(wa)
    return wa


async def delete_wrong_answer(db: AsyncSession, user_id: uuid.UUID, wa_id: uuid.UUID) -> bool:
    """Delete a wrong answer. Returns True if deleted, False if not found."""
    wa = await get_wrong_answer(db, user_id, wa_id)
    if wa is None:
        return False
    await db.delete(wa)
    await db.commit()
    return True


async def list_subjects(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    """Get distinct subject names for a user."""
    result = await db.execute(
        select(WrongAnswer.subject).where(
            WrongAnswer.user_id == user_id,
            WrongAnswer.subject.isnot(None),
        ).distinct()
    )
    return [row[0] for row in result.all() if row[0]]
