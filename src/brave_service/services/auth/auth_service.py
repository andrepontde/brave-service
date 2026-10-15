from typing import Any

from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from brave_service.api.v1.schemas.auth import TokenResponse
from brave_service.services.auth.jwt import create_access_token


PASSWORD_HASHER = PasswordHash.recommended()


def verify_password(password: str, password_hash: str) -> bool:
	return PASSWORD_HASHER.verify(password, password_hash)


class AuthService:
	def __init__(self, db: Session, user_model: Any):
		self.db = db
		self.user_model = user_model

	def authenticate_user(self, email: str, password: str) -> TokenResponse:
		user = self.db.query(self.user_model).filter(self.user_model.email == email).first()
		if user is None or not verify_password(password, user.password_hash):
			raise ValueError("Incorrect email or password")

		return TokenResponse(access_token=create_access_token(user.id))