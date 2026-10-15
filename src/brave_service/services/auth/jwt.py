import os
from datetime import datetime, timedelta, timezone

import jwt

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "brave-service"


def create_access_token(user_id: int) -> str:
	secret = os.getenv("JWT_SECRET_KEY")
	if not secret:
		raise RuntimeError("JWT_SECRET_KEY must be configured")

	now = datetime.now(timezone.utc)
	expires_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
	payload = {
		"sub": str(user_id),
		"iat": now,
		"exp": now + timedelta(minutes=expires_minutes),
		"iss": JWT_ISSUER,
	}
	return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
	secret = os.getenv("JWT_SECRET_KEY")
	if not secret:
		raise RuntimeError("JWT_SECRET_KEY must be configured")

	return jwt.decode(
		token,
		secret,
		algorithms=[JWT_ALGORITHM],
		issuer=JWT_ISSUER,
		options={"require": ["sub", "iat", "exp", "iss"]},
	)