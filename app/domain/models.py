from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from .enums import RideStatus, VehicleType

LATITUDE_MIN = -90.0
LATITUDE_MAX = 90.0
LONGITUDE_MIN = -180.0
LONGITUDE_MAX = 180.0


@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not LATITUDE_MIN <= self.latitude <= LATITUDE_MAX:
            raise ValueError(f"latitude must be between {LATITUDE_MIN} and {LATITUDE_MAX} degrees")
        if not LONGITUDE_MIN <= self.longitude <= LONGITUDE_MAX:
            raise ValueError(f"longitude must be between {LONGITUDE_MIN} and {LONGITUDE_MAX} degrees")


@dataclass
class User:
    id: UUID
    name: str
    phone: str
    roles: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RiderProfile:
    user_id: UUID
    preferences: Optional[dict[str, Any]] = None


@dataclass
class DriverProfile:
    user_id: UUID
    vehicle_type: VehicleType
    latitude: float
    longitude: float
    is_available: bool = True
    rating: float = 5.0


@dataclass
class Ride:
    id: UUID = field(default_factory=uuid4)
    rider_id: UUID = None
    driver_id: Optional[UUID] = None
    pickup: Coordinate = None
    destination: Coordinate = None
    requested_vehicle_type: VehicleType = VehicleType.SEDAN
    assigned_vehicle_type: Optional[VehicleType] = None
    status: RideStatus = RideStatus.ONGOING
    coupon_code: Optional[str] = None
    final_fare: Optional[Decimal] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


@dataclass
class Coupon:
    code: str
    discount_percentage: Decimal
    active: bool = True
