from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CreateEventCommand:
	"""Validated event data passed from the API layer to the service layer."""

	eventbrite_id: str | None
	name: str
	description: str | None
	starts_at: datetime
	ends_at: datetime | None
	venue: str | None
	status: str
	eventbrite_metadata: dict[str, Any] | None
