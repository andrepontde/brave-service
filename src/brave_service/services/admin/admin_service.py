from sqlalchemy import select
from sqlalchemy.orm import Session

from brave_service.database.models import Event

from .event_models import CreateEventCommand


class AdminService:
	def __init__(self, db: Session):
		self.db = db

	def create_event(self, command: CreateEventCommand) -> Event:
		if command.eventbrite_id is not None:
			existing_event = self.db.scalar(
				select(Event).where(Event.eventbrite_id == command.eventbrite_id)
			)
			if existing_event is not None:
				raise ValueError("An event with this eventbrite_id already exists")

		event = Event(
			eventbrite_id=command.eventbrite_id,
			name=command.name,
			description=command.description,
			starts_at=command.starts_at,
			ends_at=command.ends_at,
			venue=command.venue,
			status=command.status,
			eventbrite_metadata=command.eventbrite_metadata,
		)
		self.db.add(event)
		self.db.commit()
		self.db.refresh(event)
		return event