from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class BookingCreate(BaseModel):
    eventbrite_id: str = Field(min_length=1, max_length=255)
    event_id: int
    attendee_name: str = Field(min_length=1, max_length=255)
    attendee_email: EmailStr
    attendee_phone: str | None = Field(default=None, max_length=50)
    status: str = Field(default="pending", min_length=1, max_length=50)
    booking_reference: str = Field(min_length=1, max_length=255)
    booked_at: datetime
    eventbrite_metadata: dict[str, Any] | None = None


class EventbriteBooking(BookingCreate):
    source: str = "eventbrite"


class BookingUpdate(BaseModel):
    event_id: int | None = None
    attendee_name: str | None = Field(default=None, min_length=1, max_length=255)
    attendee_email: EmailStr | None = None
    attendee_phone: str | None = Field(default=None, max_length=50)
    status: str | None = Field(default=None, min_length=1, max_length=50)
    booking_reference: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )
    eventbrite_metadata: dict[str, Any] | None = None


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eventbrite_id: str
    event_id: int
    attendee_name: str
    attendee_email: EmailStr
    attendee_phone: str | None
    status: str
    booking_reference: str
    booked_at: datetime
    eventbrite_metadata: dict[str, Any] | None