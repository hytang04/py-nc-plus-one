from pydantic import BaseModel
from typing import Optional


class EventList(BaseModel):
    id: int
    title: str
    starts_at: str
    ends_at: str
    location: str


class EventSingle(BaseModel):
    id: int
    title: str
    description: Optional[str]
    starts_at: str
    ends_at: str
    location: str
    address: Optional[str]
    capacity: int
    created_at: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
