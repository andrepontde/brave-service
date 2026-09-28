from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from brave_service.database.models import Event
from .event_models import CreateEventCommand

from . import admin_helpers

class AdminService:
	def __init__(self, db: Session):
		self.db = db

	def create_event(self, command: CreateEventCommand) -> Event:
		if command.eventbrite_id is not None:
			# Retrieve the existing Event for the fast path; an EXISTS query is cheaper,
			# but it would not replace the commit-time uniqueness check for concurrent requests.
			existing_event = self.db.scalar(
				select(Event).where(Event.eventbrite_id == command.eventbrite_id)
			)
			if existing_event is not None:
				raise ValueError("An event with this eventbrite_id already exists")

		event = admin_helpers.event_from_command(command)
		self.db.add(event)
		try:
			self.db.commit()
		except IntegrityError as exc:
			# The database catches duplicates that pass the check above. Roll back the
			# failed transaction, then use ValueError so the router returns a conflict.
			self.db.rollback()
			raise ValueError("An event with this eventbrite_id already exists") from exc
		except Exception as exc:
			self.db.rollback()
			raise RuntimeError("Unexpected error occurred while creating event") from exc
		self.db.refresh(event)
		return event