import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

JWT_ALGORITHM = "HS256"
JWT_ISSUER = "brave-service"
revoked_tokens: dict[str, datetime] = {}


def create_access_token(user_id: int) -> str:
	secret = os.getenv("JWT_SECRET_KEY")
	if not secret:
		raise RuntimeError("JWT_SECRET_KEY must be configured")

	now = datetime.now(timezone.utc)
	expires_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
	expires_at = now + timedelta(minutes=expires_minutes)
	payload = {
		"sub": str(user_id),
		"jti": str(uuid4()),
		"iat": now,
		"exp": expires_at,
		"iss": JWT_ISSUER,
	}
	return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
	secret = os.getenv("JWT_SECRET_KEY")
	if not secret:
		raise RuntimeError("JWT_SECRET_KEY must be configured")

	payload = jwt.decode(
		token,
		secret,
		algorithms=[JWT_ALGORITHM],
		issuer=JWT_ISSUER,
		options={"require": ["sub", "jti", "iat", "exp", "iss"]},
	)
	if is_token_revoked(payload):
		raise jwt.InvalidTokenError("Token has been revoked")
	return payload


def cleanup_revoked_tokens() -> None:
	now = datetime.now(timezone.utc)
	for token_id, expires_at in list(revoked_tokens.items()):
		if expires_at <= now:
			revoked_tokens.pop(token_id, None)


def revoke_token(token: str) -> None:
	payload = decode_access_token(token)
	token_id = payload.get("jti")
	expires_at = payload.get("exp")
	if not isinstance(token_id, str) or not isinstance(expires_at, (int, float)):
		raise jwt.InvalidTokenError("Token is missing revocation claims")

	cleanup_revoked_tokens()
	revoked_tokens[token_id] = datetime.fromtimestamp(expires_at, timezone.utc)


def is_token_revoked(payload: dict[str, object]) -> bool:
	cleanup_revoked_tokens()
	token_id = payload.get("jti")
	return isinstance(token_id, str) and token_id in revoked_tokens