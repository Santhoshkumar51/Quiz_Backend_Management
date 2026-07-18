"""
Question endpoints — full CRUD for the /questions resource.

Read endpoints (GET) are public — no login needed to take a quiz.
Write endpoints (POST/PUT/DELETE) require a valid admin JWT token.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas, models
from ..auth import get_current_admin

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("/", response_model=schemas.QuestionRead, status_code=201)
def create_question(
    question: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    _admin: models.Admin = Depends(get_current_admin),
):
    """Create a new quiz question. Admin only."""
    return crud.create_question(db=db, question=question)


@router.get("/", response_model=list[schemas.QuestionRead])
def read_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: str | None = Query(None, description="Filter questions by category"),
    random_order: bool = Query(False, description="Return questions in random order (used for quiz-taking)"),
    db: Session = Depends(get_db),
):
    """List all questions with pagination, optionally filtered by category and randomized. Public."""
    return crud.get_questions(db=db, skip=skip, limit=limit, category=category, random_order=random_order)


@router.get("/categories/list", response_model=list[str])
def read_categories(db: Session = Depends(get_db)):
    """List all distinct question categories currently in the database. Public."""
    return crud.get_categories(db=db)


@router.get("/{question_id}", response_model=schemas.QuestionRead)
def read_question(question_id: int, db: Session = Depends(get_db)):
    """Get a single question by ID (includes its choices). Public."""
    db_question = crud.get_question(db=db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question


@router.put("/{question_id}", response_model=schemas.QuestionRead)
def update_question(
    question_id: int,
    question: schemas.QuestionUpdate,
    db: Session = Depends(get_db),
    _admin: models.Admin = Depends(get_current_admin),
):
    """Update a question's text or category. Admin only."""
    db_question = crud.update_question(db=db, question_id=question_id, question_data=question)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question


@router.delete("/{question_id}", response_model=schemas.QuestionRead)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    _admin: models.Admin = Depends(get_current_admin),
):
    """Delete a question and all its choices (cascade). Admin only."""
    db_question = crud.delete_question(db=db, question_id=question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_question
