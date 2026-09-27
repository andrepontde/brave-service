from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from brave_service.database.models import Event


class AdminService:
	def __init__(self, db: Session):
		self.db = db

	def create_event(
		self,
		*,
		eventbrite_id: str | None,
		name: str,
		description: str | None,
		starts_at: datetime,
		ends_at: datetime | None,
		venue: str | None,
		status: str,
		eventbrite_metadata: dict[str, Any] | None,
	) -> Event:
		if eventbrite_id is not None:
			existing_event = self.db.scalar(
			select(Event).where(Event.eventbrite_id == eventbrite_id)
		)
			if existing_event is not None:
				raise ValueError("An event with this eventbrite_id already exists")

		event = Event(
			eventbrite_id=eventbrite_id,
			name=name,
			description=description,
			starts_at=starts_at,
			ends_at=ends_at,
			venue=venue,
			status=status,
			eventbrite_metadata=eventbrite_metadata,
		)
		self.db.add(event)
		self.db.commit()
		self.db.refresh(event)
		return event