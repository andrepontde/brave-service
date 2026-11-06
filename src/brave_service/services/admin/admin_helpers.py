from typing import Any

from .event_models import CreateEventCommand, UpdateEventCommand, DeleteEventCommand
from brave_service.database.models import Event

def event_from_command(command: CreateEventCommand) -> Event:
    """Create an Event model from a CreateEventCommand."""
    return Event(
        eventbrite_id=command.eventbrite_id,
        name=command.name,
        description=command.description,
        starts_at=command.starts_at,
        ends_at=command.ends_at,
        venue=command.venue,
        status=command.status,
        eventbrite_metadata=command.eventbrite_metadata,
    )


def event_from_update(command: UpdateEventCommand) -> dict[str, Any]:
    """Return the fields supplied by an UpdateEventCommand for merging.

    Only the supplied fields are returned, so the caller can merge them onto the
    existing row instead of replacing all of it.
    """
    return {
        "name": command.name,
        "description": command.description,
        "starts_at": command.starts_at,
        "ends_at": command.ends_at,
        "venue": command.venue,
        "status": command.status,
        "eventbrite_metadata": command.eventbrite_metadata,
    }


def event_from_delete(command: DeleteEventCommand) -> Event:
    """Return the event identified by a DeleteEventCommand."""
    return Event(id=command.event_id)