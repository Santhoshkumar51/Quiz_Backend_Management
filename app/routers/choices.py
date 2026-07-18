"""
Choice endpoints — CRUD for the /choices resource.

GET is public (needed to display quiz choices). POST/PUT/DELETE require
a valid admin JWT token.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas, models
from ..auth import get_current_admin

router = APIRouter(prefix="/choices", tags=["Choices"])


@router.post("/", response_model=schemas.ChoiceRead, status_code=201)
def create_choice(
    choice: schemas.ChoiceCreate,
    db: Session = Depends(get_db),
    _admin: models.Admin = Depends(get_current_admin),
):
    """Create a new choice linked to an existing question. Admin only."""
    db_question = crud.get_question(db=db, question_id=choice.question_id)
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found — cannot attach choice")
    return crud.create_choice(db=db, choice=choice)


@router.get("/", response_model=list[schemas.ChoiceRead])
def read_choices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """List all choices with pagination. Public."""
    return crud.get_choices(db=db, skip=skip, limit=limit)


@router.put("/{choice_id}", response_model=schemas.ChoiceRead)
def update_choice(
    choice_id: int,
    choice: schemas.ChoiceUpdate,
    db: Session = Depends(get_db),
    _admin: models.Admin = Depends(get_current_admin),
):
    """Update a choice's text or correctness flag. Admin only."""
    db_choice = crud.update_choice(db=db, choice_id=choice_id, choice_data=choice)
    if db_choice is None:
        raise HTTPException(status_code=404, detail="Choice not found")
    return db_choice


@router.delete("/{choice_id}", response_model=schemas.ChoiceRead)
def delete_choice(
    choice_id: int,
    db: Session = Depends(get_db),
    _admin: models.Admin = Depends(get_current_admin),
):
    """Delete a single choice. Admin only."""
    db_choice = crud.delete_choice(db=db, choice_id=choice_id)
    if db_choice is None:
        raise HTTPException(status_code=404, detail="Choice not found")
    return db_choice
