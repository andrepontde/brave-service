import asyncio
from typing import Any
from unittest.mock import Mock

import httpx
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from brave_service.database.connection import get_db
from brave_service.main import app


def event_request() -> dict[str, Any]:
	return {
		"eventbrite_id": "event-123",
		"name": "Community meetup",
		"description": "An evening event",
		"starts_at": "2026-10-01T18:00:00Z",
		"ends_at": "2026-10-01T20:00:00Z",
		"venue": "Main hall",
		"status": "published",
		"eventbrite_metadata": {"source": "eventbrite"},
	}


async def send_create_event_request(
	db_session: Mock,
	payload: dict[str, Any],
) -> httpx.Response:
	# ASGITransport sends an HTTP request directly to the FastAPI app in memory.
	# No web server or PostgreSQL process is needed for this test.
	transport = httpx.ASGITransport(app=app)

	# FastAPI calls this function instead of the real get_db dependency. A named
	# function makes the replacement clearer than using a one-line lambda.
	def override_get_db() -> Mock:
		return db_session

	app.dependency_overrides[get_db] = override_get_db

	try:
		async with httpx.AsyncClient(
			transport=transport,
			base_url="http://test",
		) as client:
			return await client.post("/api/v1/admin/event", json=payload)
	finally:
		# Dependency overrides are global on the FastAPI app, so always remove
		# this test's override before another test starts.
		app.dependency_overrides.pop(get_db, None)


def test_create_event_returns_created_event(db_session: Mock) -> None:
	# A real database would assign this ID during refresh. This small callback
	# gives the in-memory SQLAlchemy model the same state for response testing.
	def assign_database_id(event: Any) -> None:
		event.id = 42

	db_session.refresh.side_effect = assign_database_id

	response = asyncio.run(send_create_event_request(db_session, event_request()))

	assert response.status_code == 201
	assert response.json()["id"] == 42
	assert response.json()["name"] == "Community meetup"
	db_session.add.assert_called_once()
	db_session.commit.assert_called_once_with()
	db_session.refresh.assert_called_once()


def test_create_event_returns_conflict_for_duplicate_eventbrite_id(
	db_session: Mock,
) -> None:
	# The real service converts this PostgreSQL error into an HTTP 409 response.
	db_session.commit.side_effect = IntegrityError(
		"insert event",
		{},
		UniqueViolation("duplicate eventbrite_id"),
	)

	response = asyncio.run(send_create_event_request(db_session, event_request()))

	assert response.status_code == 409
	assert response.json()["detail"] == (
		"An event with this eventbrite_id already exists"
	)
	db_session.rollback.assert_called_once_with()


def test_create_event_returns_server_error_for_database_failure(
	db_session: Mock,
) -> None:
	# This exercises the real service error handling through the HTTP endpoint.
	db_session.commit.side_effect = OSError("database unavailable")

	response = asyncio.run(send_create_event_request(db_session, event_request()))

	assert response.status_code == 500
	assert response.json()["detail"] == "Unexpected error occurred while creating event"
	db_session.rollback.assert_called_once_with()