from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from brave_service.api.v1.schemas.event import EventCreate, EventResponse
from brave_service.database.connection import get_db
from brave_service.services.admin_service import AdminService

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@admin_router.post(
    "/event",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    new_event: EventCreate,
    db: Session = Depends(get_db),
) -> EventResponse:
    try:
        return AdminService(db).create_event(**new_event.model_dump())
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error