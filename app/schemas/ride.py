from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import RideStatus, VehicleType
from app.schemas.driver import CoordinateRequest


class RideCreateRequest(BaseModel):
    rider_id: UUID
    pickup: CoordinateRequest
    destination: CoordinateRequest
    requested_vehicle_type: VehicleType = VehicleType.SEDAN
    coupon_code: str | None = None


class RideResponse(BaseModel):
    id: UUID
    rider_id: UUID
    driver_id: UUID | None = None
    pickup: CoordinateRequest
    destination: CoordinateRequest
    requested_vehicle_type: VehicleType
    assigned_vehicle_type: VehicleType | None = None
    status: RideStatus
    coupon_code: str | None = None
    final_fare: Decimal | None = None
    created_at: datetime
    completed_at: datetime | None = None
