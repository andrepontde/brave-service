from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CreateEventCommand:
	"""Request to create an event in the service layer.

	This is deliberately separate from the Pydantic API model so the service
	does not depend on HTTP or FastAPI types. ``frozen=True`` keeps the validated
	input unchanged while the service processes it.
	"""

	eventbrite_id: str | None
	name: str
	description: str | None
	starts_at: datetime
	ends_at: datetime | None
	venue: str | None
	status: str
	eventbrite_metadata: dict[str, Any] | None


@dataclass(frozen=True)
class UpdateEventCommand:
	"""Partial request to update an existing event in the service layer.

	The service layer stays independent of FastAPI types; only fields that are
	allowed to change on an update are carried here. ``frozen=True`` keeps the
	validated input unchanged while the service processes it.
	"""

	name: str | None
	description: str | None
	starts_at: datetime | None
	ends_at: datetime | None
	venue: str | None
	status: str | None
	eventbrite_metadata: dict[str, Any] | None


@dataclass(frozen=True)
class DeleteEventCommand:
	"""Request to delete an event in the service layer.

	The command carries no mutable data; it only identifies the event to remove.
	``frozen=True`` keeps the validated input unchanged while the service
	processes it.
	"""

	event_id: int
