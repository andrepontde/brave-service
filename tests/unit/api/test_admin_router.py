import asyncio
from datetime import datetime
from typing import Any
from unittest.mock import Mock

import httpx
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from brave_service.api.v1.dependencies import get_current_admin
from brave_service.database.connection import get_db
from brave_service.database.models import Admin, Event
from brave_service.database.models.event import Event as EventModel
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
	authenticated: bool = True,
) -> httpx.Response:
	# ASGITransport sends an HTTP request directly to the FastAPI app in memory.
	# No web server or PostgreSQL process is needed for this test.
	transport = httpx.ASGITransport(app=app)

	# FastAPI calls this function instead of the real get_db dependency. A named
	# function makes the replacement clearer than using a one-line lambda.
	def override_get_db() -> Mock:
		return db_session

	app.dependency_overrides[get_db] = override_get_db
	if authenticated:
		app.dependency_overrides[get_current_admin] = lambda: Admin(
			id=1,
			email="admin@example.com",
			password_hash="unused",
		)

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
		app.dependency_overrides.pop(get_current_admin, None)


def test_create_event_rejects_unauthenticated_request(db_session: Mock) -> None:
	response = asyncio.run(
		send_create_event_request(db_session, event_request(), authenticated=False),
	)

	assert response.status_code == 401
	assert response.json()["detail"] == "Not authenticated"


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


def event_detail() -> Event:
	return Event(
		id=42,
		eventbrite_id="event-123",
		name="Community meetup",
		description="An evening event",
		starts_at=datetime.fromisoformat("2026-10-01T18:00:00+00:00"),
		ends_at=datetime.fromisoformat("2026-10-01T20:00:00+00:00"),
		venue="Main hall",
		status="published",
		eventbrite_metadata={"source": "eventbrite"},
	)


def event_update() -> dict[str, Any]:
	return {
		"name": "Community meetup (updated)",
		"description": "An evening event",
		"venue": "Main hall",
		"status": "draft",
	}


async def send_event_request(
	db_session: Mock,
	method: str,
	event_id: int,
	payload: dict[str, Any] | None = None,
	authenticated: bool = True,
) -> httpx.Response:
	transport = httpx.ASGITransport(app=app)

	def override_get_db() -> Mock:
		return db_session

	app.dependency_overrides[get_db] = override_get_db
	if authenticated:
		app.dependency_overrides[get_current_admin] = lambda: Admin(
			id=1,
			email="admin@example.com",
			password_hash="unused",
		)

	try:
		async with httpx.AsyncClient(
			transport=transport,
			base_url="http://test",
		) as client:
			if payload is None:
				return await client.request(
					method, f"/api/v1/admin/event/{event_id}"
				)
			return await client.request(
				method, f"/api/v1/admin/event/{event_id}", json=payload
			)
	finally:
		app.dependency_overrides.pop(get_db, None)
		app.dependency_overrides.pop(get_current_admin, None)


def event_not_found(db_session: Mock) -> None:
	# A real database would raise here; the endpoint turns it into a 404.
	db_session.query.return_value.filter.return_value.first.return_value = None


def test_get_event_rejects_unauthenticated_request(db_session: Mock) -> None:
	response = asyncio.run(
		send_event_request(db_session, "GET", 42, authenticated=False),
	)

	assert response.status_code == 401
	assert response.json()["detail"] == "Not authenticated"


def test_get_event_returns_event(db_session: Mock) -> None:
	db_session.query.return_value.filter.return_value.first.return_value = (
		event_detail()
	)

	response = asyncio.run(send_event_request(db_session, "GET", 42))

	assert response.status_code == 200
	assert response.json() == {
		"id": 42,
		"eventbrite_id": "event-123",
		"name": "Community meetup",
		"description": "An evening event",
		"starts_at": "2026-10-01T18:00:00Z",
		"ends_at": "2026-10-01T20:00:00Z",
		"venue": "Main hall",
		"status": "published",
		"eventbrite_metadata": {"source": "eventbrite"},
	}


def test_get_event_returns_not_found(db_session: Mock) -> None:
	event_not_found(db_session)

	response = asyncio.run(send_event_request(db_session, "GET", 42))

	assert response.status_code == 404
	assert response.json()["detail"] == "Event not found"


def test_get_event_returns_server_error_for_database_failure(
	db_session: Mock,
) -> None:
	# This exercises the real service error handling through the HTTP endpoint.
	db_session.query.return_value.filter.return_value.first.side_effect = OSError(
		"database unavailable"
	)

	response = asyncio.run(send_event_request(db_session, "GET", 42))

	assert response.status_code == 500
	assert response.json()["detail"] == "Unexpected error occurred while getting event"


def test_update_event_rejects_unauthenticated_request(db_session: Mock) -> None:
	response = asyncio.run(
		send_event_request(
			db_session, "PUT", 42, payload=event_update(), authenticated=False
		),
	)

	assert response.status_code == 401
	assert response.json()["detail"] == "Not authenticated"


def test_update_event_returns_updated_event(db_session: Mock) -> None:
	event = event_detail()
	db_session.query.return_value.filter.return_value.first.return_value = (
		event
	)

	response = asyncio.run(send_event_request(db_session, "PUT", 42, payload=event_update()))

	assert response.status_code == 200
	assert response.json()["name"] == "Community meetup (updated)"
	assert response.json()["status"] == "draft"
	assert response.json()["venue"] == "Main hall"
	assert response.json()["description"] == "An evening event"
	db_session.commit.assert_called_once_with()
	db_session.refresh.assert_called_once()


def test_update_event_returns_not_found(db_session: Mock) -> None:
	event_not_found(db_session)

	response = asyncio.run(send_event_request(db_session, "PUT", 42, payload=event_update()))

	assert response.status_code == 404
	assert response.json()["detail"] == "Event not found"


def test_update_event_returns_server_error_for_database_failure(
	db_session: Mock,
) -> None:
	# This exercises the real service error handling through the HTTP endpoint.
	db_session.commit.side_effect = OSError("database unavailable")
	event = event_detail()
	db_session.query.return_value.filter.return_value.first.return_value = (
		event
	)

	response = asyncio.run(send_event_request(db_session, "PUT", 42, payload=event_update()))

	assert response.status_code == 500
	assert response.json()["detail"] == "Unexpected error occurred while updating event"


def test_delete_event_rejects_unauthenticated_request(db_session: Mock) -> None:
	response = asyncio.run(
		send_event_request(db_session, "DELETE", 42, authenticated=False),
	)

	assert response.status_code == 401
	assert response.json()["detail"] == "Not authenticated"


def test_delete_event_returns_success(db_session: Mock) -> None:
	event = event_detail()
	db_session.query.return_value.filter.return_value.first.return_value = (
		event
	)

	response = asyncio.run(send_event_request(db_session, "DELETE", 42))

	assert response.status_code == 204
	db_session.delete.assert_called_once_with(event)
	db_session.commit.assert_called_once_with()


def test_delete_event_returns_not_found(db_session: Mock) -> None:
	event_not_found(db_session)

	response = asyncio.run(send_event_request(db_session, "DELETE", 42))

	assert response.status_code == 404
	assert response.json()["detail"] == "Event not found"


def test_delete_event_returns_server_error_for_database_failure(
	db_session: Mock,
) -> None:
	# This exercises the real service error handling through the HTTP endpoint.
	db_session.commit.side_effect = OSError("database unavailable")
	event = event_detail()
	db_session.query.return_value.filter.return_value.first.return_value = (
		event
	)

	response = asyncio.run(send_event_request(db_session, "DELETE", 42))

	assert response.status_code == 500
	assert response.json()["detail"] == "Unexpected error occurred while deleting event"