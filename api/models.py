from datetime import datetime, timezone
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import Optional


class EventGetListResponse(BaseModel):
    id: int
    title: str
    starts_at: str
    ends_at: str
    location: str


class EventGetSingleResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    starts_at: str
    ends_at: str
    location: str
    address: Optional[str]
    capacity: int
    created_at: str


class EventPostRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = None
    starts_at: datetime
    ends_at: datetime
    venue_id: int

    @field_validator("starts_at", "ends_at", mode="before")
    @classmethod
    def parse_iso_datetime(cls, value: object) -> datetime:
        if not isinstance(value, str) or len(value) < 11 or value[10] not in "Tt":
            raise ValueError("Date must be an ISO 8601 string")

        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail={"code": "BAD_REQUEST",
                        "message": "Date must be a valid ISO 8601 datetime"}
            )

    @model_validator(mode="after")
    def validate_event_time_range(self) -> "EventPostRequest":
        starts_at = self.starts_at
        ends_at = self.ends_at
        if starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        if ends_at.tzinfo is None:
            ends_at = ends_at.replace(tzinfo=timezone.utc)

        if starts_at > ends_at:
            raise HTTPException(
                status_code=400,
                detail={"code": "BAD_REQUEST",
                        "message": "Start time must be before or equal to end time"}
            )
        return self


class EventPostResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    starts_at: str
    ends_at: str
    venue_id: int
    organiser_id: int
    created_at: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: str


class RSVP(BaseModel):
    id: int
    attendee_id: int
    event_id: int
    created_at: str
