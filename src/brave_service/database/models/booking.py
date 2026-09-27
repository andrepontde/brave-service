from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..connection import Base


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    eventbrite_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    attendee_name: Mapped[str] = mapped_column(String(255))
    attendee_email: Mapped[str] = mapped_column(String(320))
    attendee_phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(50),default="pending")
    booking_reference: Mapped[str] = mapped_column(String(255), index=True)
    booked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    eventbrite_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON,
        nullable=True,
    )

    event: Mapped["Event"] = relationship(back_populates="bookings")