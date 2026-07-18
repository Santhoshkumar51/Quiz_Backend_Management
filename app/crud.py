"""
CRUD (Create, Read, Update, Delete) operations for Questions and Choices.
All functions accept a SQLAlchemy Session and return ORM model instances.
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models, schemas


# ── Question CRUD ─────────────────────────────────────────────────────────────

def create_question(db: Session, question: schemas.QuestionCreate) -> models.Question:
    db_question = models.Question(
        question_text=question.question_text,
        category=question.category,
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def get_questions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: str | None = None,
    random_order: bool = False,
) -> list[models.Question]:
    query = db.query(models.Question)
    if category:
        query = query.filter(models.Question.category == category)
    if random_order:
        # func.random() maps to SQLite's RANDOM() and PostgreSQL's RANDOM() alike
        query = query.order_by(func.random())
    return query.offset(skip).limit(limit).all()


def get_categories(db: Session) -> list[str]:
    rows = db.query(models.Question.category).distinct().all()
    return sorted({row[0] for row in rows if row[0]})


def get_question(db: Session, question_id: int) -> models.Question | None:
    return db.query(models.Question).filter(models.Question.id == question_id).first()


def update_question(
    db: Session, question_id: int, question_data: schemas.QuestionUpdate
) -> models.Question | None:
    db_question = get_question(db, question_id)
    if db_question is None:
        return None
    update_fields = question_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(db_question, field, value)
    db.commit()
    db.refresh(db_question)
    return db_question


def delete_question(db: Session, question_id: int) -> models.Question | None:
    db_question = get_question(db, question_id)
    if db_question is None:
        return None
    db.delete(db_question)  # cascade deletes choices
    db.commit()
    return db_question


# ── Choice CRUD ───────────────────────────────────────────────────────────────

def create_choice(db: Session, choice: schemas.ChoiceCreate) -> models.Choice:
    db_choice = models.Choice(
        choice_text=choice.choice_text,
        is_correct=choice.is_correct,
        question_id=choice.question_id,
    )
    db.add(db_choice)
    db.commit()
    db.refresh(db_choice)
    return db_choice


def get_choices(db: Session, skip: int = 0, limit: int = 100) -> list[models.Choice]:
    return db.query(models.Choice).offset(skip).limit(limit).all()


def get_choice(db: Session, choice_id: int) -> models.Choice | None:
    return db.query(models.Choice).filter(models.Choice.id == choice_id).first()


def update_choice(
    db: Session, choice_id: int, choice_data: schemas.ChoiceUpdate
) -> models.Choice | None:
    db_choice = get_choice(db, choice_id)
    if db_choice is None:
        return None
    update_fields = choice_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(db_choice, field, value)
    db.commit()
    db.refresh(db_choice)
    return db_choice


def delete_choice(db: Session, choice_id: int) -> models.Choice | None:
    db_choice = get_choice(db, choice_id)
    if db_choice is None:
        return None
    db.delete(db_choice)
    db.commit()
    return db_choice
