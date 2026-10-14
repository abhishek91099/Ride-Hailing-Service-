from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import VehicleType


class CoordinateRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class DriverCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    phone: str = Field(..., min_length=7, max_length=20)
    vehicle_type: VehicleType
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    rating: float = Field(default=5.0, ge=0.0, le=5.0)


class DriverLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


class DriverProfileResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    vehicle_type: VehicleType
    latitude: float
    longitude: float
    is_available: bool
    rating: float
    created_at: datetime
