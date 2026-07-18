"""
Pydantic schemas for request validation and response serialization.
Separate Create (input) and Read (output) schemas per entity.
"""

from pydantic import BaseModel


# ── Choice Schemas ────────────────────────────────────────────────────────────

class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool = False


class ChoiceCreate(ChoiceBase):
    question_id: int


class ChoiceRead(ChoiceBase):
    id: int
    question_id: int

    model_config = {"from_attributes": True}


class ChoiceUpdate(BaseModel):
    choice_text: str | None = None
    is_correct: bool | None = None


# ── Question Schemas ──────────────────────────────────────────────────────────

class QuestionBase(BaseModel):
    question_text: str
    category: str | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: int
    choices: list[ChoiceRead] = []

    model_config = {"from_attributes": True}


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    category: str | None = None


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class AdminLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
