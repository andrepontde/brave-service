from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from brave_service.database.models import Event
from .event_models import (
	CreateEventCommand,
	UpdateEventCommand,
	DeleteEventCommand,
)

from . import admin_helpers

class AdminService:
	def __init__(self, db: Session):
		self.db = db

	def create_event(self, command: CreateEventCommand) -> Event:
		event = admin_helpers.event_from_command(command)
		self.db.add(event)
		try:
			self.db.commit()
		except IntegrityError as exc:
			self.db.rollback()
			# PostgreSQL uses UniqueViolation for duplicate IDs; other integrity errors
			# are unexpected and should not be reported as a conflict.
			if isinstance(exc.orig, UniqueViolation):
				raise ValueError(
					"An event with this eventbrite_id already exists"
				) from exc
			raise RuntimeError(
				"Unexpected database integrity error while creating event"
			) from exc
		except Exception as exc:
			self.db.rollback()
			raise RuntimeError("Unexpected error occurred while creating event") from exc
		self.db.refresh(event)
		return event

	def get_event(self, event_id: int) -> Event:
		try:
			event = self.db.query(Event).filter(Event.id == event_id).first()
		except OSError as error:
			raise RuntimeError(
				"Unexpected error occurred while getting event",
			) from error
		if event is None:
			raise ValueError("Event not found")
		return event

	def update_event(self, event_id: int, command: UpdateEventCommand) -> Event:
		event = self.get_event(event_id)
		if not command.name and not command.description and not command.starts_at and not command.ends_at and not command.venue and not command.status and not command.eventbrite_metadata:
			return event

		# Merge the supplied fields onto the existing row so unchanged fields
		# retain their previous values.
		for field, value in admin_helpers.event_from_update(command).items():
			if value is not None:
				setattr(event, field, value)

		try:
			self.db.commit()
			self.db.refresh(event)
		except OSError as error:
			raise RuntimeError(
				"Unexpected error occurred while updating event",
			) from error
		return event

	def delete_event(self, event_id: int) -> None:
		# Load the row through the query layer so the handler can rely on the
		# same error handling as the other methods.
		event = self.get_event(event_id)
		self.db.delete(event)
		try:
			self.db.commit()
		except OSError as error:
			raise RuntimeError(
				"Unexpected error occurred while deleting event",
			) from error
		return None