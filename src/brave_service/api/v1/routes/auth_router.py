from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from brave_service.api.v1.schemas.auth import TokenResponse, LoginRequest
from brave_service.database.connection import get_db
from brave_service.database.models import Admin
from brave_service.services.auth.auth_service import AuthService
from brave_service.services.auth.jwt import revoke_token


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
security = HTTPBearer()

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login(
    login_request: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    try:
        return AuthService(db, Admin).authenticate_user(
            login_request.email,
            login_request.password,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


@auth_router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> None:
    try:
        revoke_token(credentials.credentials)
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
