"""
One-time seed script — loads data/questions.csv into quiz.db.

Run from the project root with:
    python -m app.seed_data

Skips seeding if the questions table already has data, so it's safe to
run multiple times without creating duplicates.
"""

import csv
import os

from .database import Base, engine, SessionLocal
from . import models

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "questions.csv")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_count = db.query(models.Question).count()
        if existing_count > 0:
            print(f"Database already has {existing_count} questions. Skipping seed.")
            return

        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            question_count = 0
            choice_count = 0

            for row in reader:
                db_question = models.Question(
                    question_text=row["question_text"].strip(),
                    category=row["category"].strip(),
                )
                db.add(db_question)
                db.flush()  # assigns db_question.id before we create choices

                choice_texts = [
                    row["choice_1"].strip(),
                    row["choice_2"].strip(),
                    row["choice_3"].strip(),
                    row["choice_4"].strip(),
                ]
                correct_index = int(row["correct_index"])

                for i, choice_text in enumerate(choice_texts):
                    db.add(
                        models.Choice(
                            choice_text=choice_text,
                            is_correct=(i == correct_index),
                            question_id=db_question.id,
                        )
                    )
                    choice_count += 1

                question_count += 1

            db.commit()
            print(f"Seeded {question_count} questions and {choice_count} choices into quiz.db")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
