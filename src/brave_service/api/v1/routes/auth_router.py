from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from brave_service.api.v1.schemas.auth import TokenResponse, LoginRequest
from brave_service.database.connection import get_db
from brave_service.services.admin.auth_service import AuthService


auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

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
        return AuthService(db).authenticate_user(
            login_request.email,
            login_request.password,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
