from getpass import getpass

from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from brave_service.database.connection import SessionLocal
from brave_service.database.models import Admin

PASSWORD_HASHER = PasswordHash.recommended()
MINIMUM_PASSWORD_LENGTH = 12


def create_admin_account(db: Session, email: str, password: str) -> Admin:
    normalized_email = email.strip().casefold()
    if not normalized_email:
        raise ValueError("Email is required")
    if len(password) < MINIMUM_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MINIMUM_PASSWORD_LENGTH} characters"
        )

    admin = Admin(
        email=normalized_email,
        password_hash=PASSWORD_HASHER.hash(password),
    )
    db.add(admin)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise ValueError("An account with that email already exists") from error

    db.refresh(admin)
    return admin


def main() -> None:
    email = input("Admin email: ").strip()
    password = getpass("Password: ")
    confirmation = getpass("Confirm password: ")

    if password != confirmation:
        raise SystemExit("Passwords do not match")

    try:
        with SessionLocal() as db:
            admin = create_admin_account(db, email, password)
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print(f"Created admin account for {admin.email}")


if __name__ == "__main__":
    main()
