from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from brave_service.api.v1.dependencies import get_current_admin
from brave_service.api.v1.schemas.event import (
    EventCreate,
    EventResponse,
    EventUpdate,
    EventResponse as EventDetailResponse,
)
from brave_service.database.models import Admin
from brave_service.database.connection import get_db
from brave_service.services.admin import AdminService
from brave_service.services.admin.event_models import (
    CreateEventCommand,
    UpdateEventCommand,
    DeleteEventCommand,
)

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


def _event_detail(event: EventDetailResponse) -> EventDetailResponse:
    """Return the event unchanged; kept so the response model stays explicit."""
    return event


def _event_not_found(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


# Create a new event. Returns the created event.
@admin_router.post(
    "/event",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_event(
    new_event: EventCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> EventResponse:
    try:
        # unpack the EventCreate model into a CreateEventCommand, then pass it to the AdminService
        command = CreateEventCommand(**new_event.model_dump())
        return AdminService(db).create_event(command)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


# Fetch a single event. Returns the event.
@admin_router.get(
    "/event/{event_id}",
    response_model=EventResponse,
)
def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> EventResponse:
    try:
        event = AdminService(db).get_event(event_id)
        return EventResponse.model_validate(event)
    except ValueError as error:
        raise _event_not_found(str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


# Update an event. Partial fields are merged onto the existing row.
# Returns the updated event.
@admin_router.put(
    "/event/{event_id}",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
)
def update_event(
    event_id: int,
    update_event: EventUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> EventResponse:
    try:
        command = UpdateEventCommand(
            name=update_event.name,
            description=update_event.description,
            starts_at=update_event.starts_at,
            ends_at=update_event.ends_at,
            venue=update_event.venue,
            status=update_event.status,
            eventbrite_metadata=update_event.eventbrite_metadata,
        )
        return AdminService(db).update_event(event_id, command)
    except ValueError as error:
        raise _event_not_found(str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error


# Delete an event.
@admin_router.delete(
    "/event/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> None:
    try:
        AdminService(db).delete_event(event_id)
        return None
    except ValueError as error:
        raise _event_not_found(str(error))
    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
        ) from error