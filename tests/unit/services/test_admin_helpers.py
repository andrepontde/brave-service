from datetime import datetime, timezone

from brave_service.database.models import Event
from brave_service.services.admin.admin_helpers import event_from_command
from brave_service.services.admin.event_models import CreateEventCommand


def test_event_from_command_copies_every_event_field() -> None:
	starts_at = datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc)
	ends_at = datetime(2026, 10, 1, 20, 0, tzinfo=timezone.utc)
	command = CreateEventCommand(
		eventbrite_id="event-123",
		name="Community meetup",
		description="An evening event",
		starts_at=starts_at,
		ends_at=ends_at,
		venue="Main hall",
		status="draft",
		eventbrite_metadata={"source": "eventbrite"},
	)

	event = event_from_command(command)

	assert isinstance(event, Event)
	assert event.eventbrite_id == "event-123"
	assert event.name == "Community meetup"
	assert event.description == "An evening event"
	assert event.starts_at == starts_at
	assert event.ends_at == ends_at
	assert event.venue == "Main hall"
	assert event.status == "draft"
	assert event.eventbrite_metadata == {"source": "eventbrite"}


def test_event_from_command_preserves_optional_none_values() -> None:
	command = CreateEventCommand(
		eventbrite_id=None,
		name="Community meetup",
		description=None,
		starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		ends_at=None,
		venue=None,
		status="published",
		eventbrite_metadata=None,
	)

	event = event_from_command(command)

	assert event.eventbrite_id is None
	assert event.description is None
	assert event.ends_at is None
	assert event.venue is None
	assert event.eventbrite_metadata is None
