"""
FastAPI application entrypoint.
Creates database tables on startup, auto-seeds quiz questions, auto-creates
an admin account from env vars if one doesn't exist yet, and registers routers.
"""

import os

from fastapi import FastAPI

from .database import Base, engine, SessionLocal
from . import models, auth  # noqa: F401  (models import ensures tables register on Base)
from .routers import questions, choices, auth as auth_router
from .seed_data import seed

# Create tables if they don't already exist (no manual DB setup needed)
Base.metadata.create_all(bind=engine)

# Auto-seed quiz questions on startup — seed() skips silently if data already exists,
# so this keeps the app self-healing on hosts with ephemeral disks (e.g. Render free tier)
seed()


def _ensure_admin_from_env():
    """
    If ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD are set as environment
    variables and no admin exists yet, create one automatically. This lets a
    deploy host (Render, etc.) provision your admin account without shell
    access — set these three env vars once in the host's dashboard.
    Locally, use `python -m app.create_admin` instead; env vars are optional.
    """
    username = os.getenv("ADMIN_USERNAME")
    email = os.getenv("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD")

    if not (username and email and password):
        return  # nothing to do locally unless you set these

    db = SessionLocal()
    try:
        existing = db.query(models.Admin).filter(models.Admin.username == username).first()
        if existing:
            return
        db.add(
            models.Admin(
                username=username,
                email=email,
                hashed_password=auth.hash_password(password),
            )
        )
        db.commit()
    finally:
        db.close()


_ensure_admin_from_env()

app = FastAPI(
    title="Quiz Backend Management API",
    version="1.0",  # required by the OpenAPI spec; kept minimal
    description="A RESTful API for managing Data Science quiz questions and answer choices.",
    # Trim down the default Swagger UI: collapse the Schemas section, keep endpoint list compact
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # hides the "Schemas" section entirely
        "docExpansion": "list",          # endpoints listed, not auto-expanded
        "displayRequestDuration": True,
        "syntaxHighlight.theme": "obsidian",
    },
)

app.include_router(auth_router.router)
app.include_router(questions.router)
app.include_router(choices.router)


@app.get("/", tags=["Root"])
def read_root():
    """Health check / welcome route."""
    return {
        "message": "Quiz Backend Management API is running.",
        "docs": "/docs",
    }
