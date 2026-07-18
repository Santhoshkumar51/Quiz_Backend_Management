"""
Run this once to create your admin account locally.

    python -m app.create_admin

It will prompt for a username, email, and password, then store the
hashed password in the admins table. There is no public API endpoint
for this — it's intentionally a manual, local-only step so nobody else
can create an admin account.
"""

import getpass

from .database import Base, engine, SessionLocal
from . import models, auth


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        username = input("Admin username: ").strip()
        email = input("Admin email: ").strip()
        password = getpass.getpass("Admin password: ")
        confirm = getpass.getpass("Confirm password: ")

        if password != confirm:
            print("Passwords do not match. Aborted.")
            return

        existing = db.query(models.Admin).filter(models.Admin.username == username).first()
        if existing:
            print(f"An admin with username '{username}' already exists. Aborted.")
            return

        admin = models.Admin(
            username=username,
            email=email,
            hashed_password=auth.hash_password(password),
        )
        db.add(admin)
        db.commit()
        print(f"Admin account '{username}' created successfully.")

    finally:
        db.close()


if __name__ == "__main__":
    main()
