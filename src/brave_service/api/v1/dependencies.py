from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from brave_service.database.connection import get_db
from brave_service.database.models import Admin
from brave_service.services.admin.jwt import decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def get_current_admin(
	token: Annotated[str, Depends(oauth2_scheme)],
	db: Session = Depends(get_db),
) -> Admin:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	try:
		payload = decode_access_token(token)
		admin_id = int(payload["sub"])
	except (jwt.InvalidTokenError, KeyError, TypeError, ValueError) as error:
		raise credentials_exception from error

	admin = db.query(Admin).filter(Admin.id == admin_id).first()
	if admin is None:
		raise credentials_exception

	return admin
