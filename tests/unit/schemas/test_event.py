
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from brave_service.api.v1.schemas.event import EventCreate, EventResponse, EventUpdate


def test_event_create_uses_published_as_the_default_status() -> None:
	event = EventCreate(
		name="Community meetup",
		starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
	)

	assert event.status == "published"


def test_event_create_accepts_all_supported_fields() -> None:
	starts_at = datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc)
	ends_at = datetime(2026, 10, 1, 20, 0, tzinfo=timezone.utc)

	event = EventCreate(
		eventbrite_id="event-123",
		name="Community meetup",
		description="An evening event",
		starts_at=starts_at,
		ends_at=ends_at,
		venue="Main hall",
		status="draft",
		eventbrite_metadata={"source": "eventbrite"},
	)

	assert event.eventbrite_id == "event-123"
	assert event.name == "Community meetup"
	assert event.description == "An evening event"
	assert event.starts_at == starts_at
	assert event.ends_at == ends_at
	assert event.venue == "Main hall"
	assert event.status == "draft"
	assert event.eventbrite_metadata == {"source": "eventbrite"}


def test_event_create_requires_a_name() -> None:
	with pytest.raises(ValidationError):
		EventCreate(
			starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		)


def test_event_create_requires_a_start_time() -> None:
	with pytest.raises(ValidationError):
		EventCreate(name="Community meetup")


def test_event_create_rejects_an_empty_name() -> None:
	with pytest.raises(ValidationError):
		EventCreate(
			name="",
			starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		)


def test_event_create_rejects_a_name_longer_than_255_characters() -> None:
	with pytest.raises(ValidationError):
		EventCreate(
			name="x" * 256,
			starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		)


def test_event_create_rejects_an_empty_eventbrite_id() -> None:
	with pytest.raises(ValidationError):
		EventCreate(
			eventbrite_id="",
			name="Community meetup",
			starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		)


def test_event_update_allows_a_partial_update() -> None:
	update = EventUpdate(name="Updated meetup")

	assert update.name == "Updated meetup"
	assert update.description is None
	assert update.starts_at is None
	assert update.status is None


def test_event_update_rejects_an_empty_status() -> None:
	with pytest.raises(ValidationError):
		EventUpdate(status="")


def test_event_response_reads_attributes_from_an_event_object() -> None:
	event = SimpleNamespace(
		id=42,
		eventbrite_id="event-123",
		name="Community meetup",
		description=None,
		starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		ends_at=None,
		venue="Main hall",
		status="published",
		eventbrite_metadata={"source": "eventbrite"},
	)

	response = EventResponse.model_validate(event)

	assert response.id == 42
	assert response.name == "Community meetup"
	assert response.eventbrite_metadata == {"source": "eventbrite"}