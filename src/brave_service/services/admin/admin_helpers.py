from .event_models import CreateEventCommand
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