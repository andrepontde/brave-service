from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from brave_service.database.models import Event
from brave_service.services.admin import AdminService
from brave_service.services.admin.event_models import CreateEventCommand


def event_command() -> CreateEventCommand:
	return CreateEventCommand(
		eventbrite_id="event-123",
		name="Community meetup",
		description="An evening event",
		starts_at=datetime(2026, 10, 1, 18, 0, tzinfo=timezone.utc),
		ends_at=datetime(2026, 10, 1, 20, 0, tzinfo=timezone.utc),
		venue="Main hall",
		status="published",
		eventbrite_metadata={"source": "eventbrite"},
	)


def test_create_event_adds_commits_refreshes_and_returns_event(db_session: Mock) -> None:
	# The service depends on a SQLAlchemy session, but this unit test must not
	# connect to PostgreSQL. spec=Session prevents calls to unknown methods.

	result = AdminService(db_session).create_event(event_command())

	assert isinstance(result, Event)
	assert result.name == "Community meetup"
	db_session.add.assert_called_once_with(result)
	db_session.commit.assert_called_once_with()
	db_session.refresh.assert_called_once_with(result)
	db_session.rollback.assert_not_called()


def test_create_event_turns_duplicate_eventbrite_id_into_value_error(
	db_session: Mock,
) -> None:
	# Make commit behave like PostgreSQL when a unique eventbrite_id is reused.
	db_session.commit.side_effect = IntegrityError(
		"insert event",
		{},
		UniqueViolation("duplicate eventbrite_id"),
	)

	with pytest.raises(ValueError, match="eventbrite_id already exists"):
		AdminService(db_session).create_event(event_command())

	db_session.rollback.assert_called_once_with()
	db_session.refresh.assert_not_called()


def test_create_event_turns_other_integrity_errors_into_runtime_error(
	db_session: Mock,
) -> None:
	# An IntegrityError without UniqueViolation represents another database
	# constraint failure and should follow the service's generic error path.
	db_session.commit.side_effect = IntegrityError(
		"insert event",
		{},
		Exception("unexpected constraint"),
	)

	with pytest.raises(RuntimeError, match="Unexpected database integrity error"):
		AdminService(db_session).create_event(event_command())

	db_session.rollback.assert_called_once_with()
	db_session.refresh.assert_not_called()


def test_create_event_turns_unexpected_errors_into_runtime_error(
	db_session: Mock,
) -> None:
	# Simulate a non-IntegrityError failure such as a lost database connection.
	db_session.commit.side_effect = OSError("database unavailable")

	with pytest.raises(RuntimeError, match="Unexpected error occurred"):
		AdminService(db_session).create_event(event_command())

	db_session.rollback.assert_called_once_with()
	db_session.refresh.assert_not_called()
