"""Promote a user to admin by email. Run from the backend/ directory with
the virtualenv activated:  python ../scripts/seed_admin.py user@example.com
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.db.database import SessionLocal
from app.db import models


def main():
    if len(sys.argv) != 2:
        print("Usage: python seed_admin.py <email>")
        sys.exit(1)

    email = sys.argv[1]
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        print(f"No user found with email {email}")
        sys.exit(1)
    user.is_admin = True
    db.commit()
    print(f"{email} is now an admin.")


if __name__ == "__main__":
    main()
