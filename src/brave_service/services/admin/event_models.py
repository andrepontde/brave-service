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
