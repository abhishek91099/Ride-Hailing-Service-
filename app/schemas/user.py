from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone: str = Field(..., min_length=7, max_length=20)
    roles: list[str] = Field(default_factory=list)


class UserResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    roles: list[str]
    created_at: datetime
