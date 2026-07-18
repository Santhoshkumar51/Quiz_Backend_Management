"""
SQLAlchemy ORM models for Question and Choice.
One-to-many relationship: Question → Choices (cascade delete).
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(String, nullable=False)
    category = Column(String, nullable=True)

    # One question → many choices; deleting a question cascade-deletes its choices
    choices = relationship(
        "Choice",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="joined",
    )


class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)

    question = relationship("Question", back_populates="choices")


class Admin(Base):
    """
    Admin accounts. There is no public self-registration endpoint —
    accounts are created only via app/create_admin.py (locally) or
    auto-created from ADMIN_* environment variables on startup (for deploys).
    Table supports multiple admins even though the project currently uses one.
    """

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
