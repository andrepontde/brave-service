from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from brave_service.api.v1.schemas.auth import TokenResponse
from brave_service.database.models import Admin
from brave_service.services.admin.jwt import create_access_token, verify_password

PASSWORD_HASHER = PasswordHash.recommended()

def verify_password(password: str, password_hash: str) -> bool:
	return PASSWORD_HASHER.verify(password, password_hash)

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email: str, password: str) -> TokenResponse:
        admin = self.db.query(Admin).filter(Admin.email == email).first()
        if admin is None or not verify_password(password, admin.password_hash):
            raise ValueError("Incorrect email or password")

        return TokenResponse(access_token=create_access_token(admin.id))

