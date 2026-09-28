from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from brave_service.database.models import Event
from .event_models import CreateEventCommand

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