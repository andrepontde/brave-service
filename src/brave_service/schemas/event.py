from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    eventbrite_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime
    ends_at: datetime | None = None
    venue: str | None = Field(default=None, max_length=255)
    status: str = Field(default="published", min_length=1, max_length=50)
    eventbrite_metadata: dict[str, Any] | None = None


class EventUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    venue: str | None = Field(default=None, max_length=255)
    status: str | None = Field(default=None, min_length=1, max_length=50)
    eventbrite_metadata: dict[str, Any] | None = None


class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    eventbrite_id: str
    name: str
    description: str | None
    starts_at: datetime
    ends_at: datetime | None
    venue: str | None
    status: str
    eventbrite_metadata: dict[str, Any] | None