from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

import brave_service.api.v1.routes.admin_router as admin_router
from brave_service.api.v1.schemas.event import EventCreate
from brave_service.database.models import Event
from brave_service.services.admin import AdminService
from brave_service.services.admin.event_models import CreateEventCommand


def event_request() -> EventCreate:
	return EventCreate(
		eventbrite_id="event-123",
		name="Community meetup",
		description="An evening event",
		starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		ends_at=datetime(2026, 10, 1, 20, 0, tzinfo=timezone.utc),
		venue="Main hall",
		status="published",
		eventbrite_metadata={"source": "eventbrite"},
	)


def test_create_event_passes_a_command_to_the_service(
	monkeypatch: pytest.MonkeyPatch,
	db_session: Mock,
) -> None:
	created_event = Event(
		name="Community meetup",
		starts_at=event_request().starts_at,
	)
	service = Mock(spec=AdminService)
	service.create_event.return_value = created_event

	# Patch the dependency where the router looks it up, not its original module.
	monkeypatch.setattr(admin_router, "AdminService", Mock(return_value=service))

	result = admin_router.create_event(event_request(), db_session)

	assert result is created_event
	command = service.create_event.call_args.args[0]
	assert isinstance(command, CreateEventCommand)
	assert command.name == "Community meetup"
	assert command.eventbrite_metadata == {"source": "eventbrite"}
	service.create_event.assert_called_once_with(command)


def test_create_event_returns_conflict_for_value_error(
	monkeypatch: pytest.MonkeyPatch,
	db_session: Mock,
) -> None:
	service = Mock(spec=AdminService)
	service.create_event.side_effect = ValueError("event already exists")
	monkeypatch.setattr(admin_router, "AdminService", Mock(return_value=service))

	with pytest.raises(HTTPException) as raised:
		admin_router.create_event(event_request(), db_session)

	assert raised.value.status_code == 409
	assert raised.value.detail == "event already exists"


def test_create_event_returns_server_error_for_runtime_error(
	monkeypatch: pytest.MonkeyPatch,
	db_session: Mock,
) -> None:
	service = Mock(spec=AdminService)
	service.create_event.side_effect = RuntimeError("database unavailable")
	monkeypatch.setattr(admin_router, "AdminService", Mock(return_value=service))

	with pytest.raises(HTTPException) as raised:
		admin_router.create_event(event_request(), db_session)

	assert raised.value.status_code == 500
	assert raised.value.detail == "database unavailable"
