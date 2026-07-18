"""
Authentication endpoint. There is intentionally no /auth/register route —
admin accounts are provisioned only via app/create_admin.py or the
ADMIN_* startup env vars, never through the public API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import schemas, auth
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.AdminLogin, db: Session = Depends(get_db)):
    """Log in as an admin and receive a JWT bearer token."""
    admin = auth.authenticate_admin(db, credentials.username, credentials.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token(data={"sub": admin.username})
    return schemas.Token(access_token=access_token)
