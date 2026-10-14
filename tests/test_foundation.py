from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.enums import RideStatus, VehicleType
from app.domain.models import Coordinate, Coupon, DriverProfile, Ride, RiderProfile, User


def test_domain_models_can_be_instantiated():
    user = User(id=uuid4(), name="Alice", phone="9999999999", roles=["rider"])
    rider_profile = RiderProfile(user_id=user.id, preferences={"preferred_language": "en"})
    driver_profile = DriverProfile(
        user_id=uuid4(),
        vehicle_type=VehicleType.SEDAN,
        latitude=12.9716,
        longitude=77.5946,
        is_available=True,
        rating=4.8,
    )
    coupon = Coupon(code="SAVE10", discount_percentage=Decimal("10"), active=True)
    ride = Ride(
        id=uuid4(),
        rider_id=user.id,
        driver_id=driver_profile.user_id,
        pickup=Coordinate(latitude=12.9716, longitude=77.5946),
        destination=Coordinate(latitude=12.9958, longitude=77.6210),
        requested_vehicle_type=VehicleType.HATCHBACK,
        assigned_vehicle_type=VehicleType.SEDAN,
        status=RideStatus.ONGOING,
        coupon_code=coupon.code,
        created_at=datetime.now(timezone.utc),
    )

    assert user.roles == ["rider"]
    assert rider_profile.preferences["preferred_language"] == "en"
    assert driver_profile.vehicle_type is VehicleType.SEDAN
    assert ride.status is RideStatus.ONGOING
    assert coupon.discount_percentage == Decimal("10")


def test_coordinate_validation_rejects_invalid_values():
    with pytest.raises(ValueError):
        Coordinate(latitude=91.0, longitude=0.0)

    with pytest.raises(ValueError):
        Coordinate(latitude=0.0, longitude=181.0)


def test_app_exposes_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
