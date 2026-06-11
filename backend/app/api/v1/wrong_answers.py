"""Wrong-answer book API endpoints (quarterly plan required)."""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..deps import get_db, get_current_user
from ...middleware.subscription import require_quarterly
from ...models.user import User
from ...services import wrong_answer_svc

router = APIRouter()


# --- Schemas (inline to keep the module slim) ---
from pydantic import BaseModel
from datetime import datetime


class WrongAnswerCreate(BaseModel):
    subject: str | None = None
    question: str
    answer: str | None = None
    correct_answer: str | None = None
    tags: list[str] = []


class WrongAnswerUpdate(BaseModel):
    subject: str | None = None
    question: str | None = None
    answer: str | None = None
    correct_answer: str | None = None
    tags: list[str] | None = None


class WrongAnswerRead(BaseModel):
    id: uuid.UUID
    subject: str | None = None
    question: str
    answer: str | None = None
    correct_answer: str | None = None
    tags: list
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WrongAnswerList(BaseModel):
    items: list[WrongAnswerRead]
    total: int
    page: int
    page_size: int


class GenerateSimilarRequest(BaseModel):
    question: str
    answer: str = ""
    subject: str | None = None


class GenerateSimilarResponse(BaseModel):
    original_question: str
    similar_question: str
    answer: str | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/wrong-answers", response_model=WrongAnswerList)
async def list_answers(
    subject: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quarterly: User = Depends(require_quarterly),
):
    """List current user's wrong answers (quarterly plan only)."""
    result = await wrong_answer_svc.list_wrong_answers(
        db, current_user.id, subject=subject, page=page, page_size=page_size
    )
    return WrongAnswerList(**result)


@router.post("/wrong-answers", response_model=WrongAnswerRead, status_code=201)
async def create_answer(
    body: WrongAnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quarterly: User = Depends(require_quarterly),
):
    """Add a wrong answer."""
    wa = await wrong_answer_svc.create_wrong_answer(
        db,
        user_id=current_user.id,
        subject=body.subject,
        question=body.question,
        answer=body.answer,
        correct_answer=body.correct_answer,
        tags=body.tags,
    )
    return WrongAnswerRead.model_validate(wa)


@router.get("/wrong-answers/{answer_id}", response_model=WrongAnswerRead)
async def get_answer(
    answer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quarterly: User = Depends(require_quarterly),
):
    """Get a single wrong answer detail."""
    wa = await wrong_answer_svc.get_wrong_answer(db, current_user.id, answer_id)
    if wa is None:
        raise HTTPException(status_code=404, detail="Wrong answer not found")
    return WrongAnswerRead.model_validate(wa)


@router.put("/wrong-answers/{answer_id}", response_model=WrongAnswerRead)
async def update_answer(
    answer_id: uuid.UUID,
    body: WrongAnswerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quarterly: User = Depends(require_quarterly),
):
    """Update a wrong answer entry."""
    wa = await wrong_answer_svc.update_wrong_answer(
        db,
        current_user.id,
        answer_id,
        **body.model_dump(exclude_none=True),
    )
    if wa is None:
        raise HTTPException(status_code=404, detail="Wrong answer not found")
    return WrongAnswerRead.model_validate(wa)


@router.delete("/wrong-answers/{answer_id}", status_code=204)
async def delete_answer(
    answer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quarterly: User = Depends(require_quarterly),
):
    """Delete a wrong answer."""
    deleted = await wrong_answer_svc.delete_wrong_answer(db, current_user.id, answer_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Wrong answer not found")


@router.post("/wrong-answers/generate-similar", response_model=GenerateSimilarResponse)
async def generate_similar_question(
    body: GenerateSimilarRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _quarterly: User = Depends(require_quarterly),
):
    """Ask Claude to generate a similar practice question (quarterly plan only)."""
    from ...services.ai_engine import generate_similar_question as ai_gen

    try:
        result = await ai_gen(body.question, body.answer, body.subject or "")

        return GenerateSimilarResponse(
            original_question=body.question,
            similar_question=result.get("question", ""),
            answer=result.get("answer", ""),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")
