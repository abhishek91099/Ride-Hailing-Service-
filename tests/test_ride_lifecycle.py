from uuid import uuid4

import pytest

from app.core.exceptions import InvalidCouponError
from app.domain.enums import RideStatus, VehicleType
from app.domain.models import Coordinate, DriverProfile
from app.repositories.memory.coupon_repository import InMemoryCouponRepository
from app.repositories.memory.driver_repository import InMemoryDriverRepository
from app.repositories.memory.ride_repository import InMemoryRideRepository
from app.services.coupon_service import CouponService
from app.services.matching_service import InMemoryMatchingService
from app.services.pricing_service import PricingService
from app.services.ride_service import RideService


def test_ride_creation_assigns_driver_and_applies_coupon_discount():
    driver_repository = InMemoryDriverRepository()
    ride_repository = InMemoryRideRepository()
    coupon_repository = InMemoryCouponRepository()
    matching_service = InMemoryMatchingService(driver_repository)
    coupon_service = CouponService(coupon_repository)
    service = RideService(ride_repository, driver_repository, matching_service, coupon_service)

    driver = DriverProfile(
        user_id=uuid4(),
        vehicle_type=VehicleType.SEDAN,
        latitude=12.9710,
        longitude=77.5930,
        is_available=True,
    )
    driver_repository.add(driver)
    coupon_service.create_coupon(code="SAVE10", discount_percentage=10, active=True)

    ride = service.create_ride(
        rider_id=uuid4(),
        pickup=Coordinate(12.9700, 77.5900),
        destination=Coordinate(12.9800, 77.6000),
        requested_vehicle_type=VehicleType.SEDAN,
        coupon_code="SAVE10",
    )

    assert ride.status is RideStatus.ONGOING
    assert ride.driver_id == driver.user_id
    assert ride.final_fare == 45.00
    assert driver_repository.get_by_user_id(driver.user_id).is_available is False


def test_ride_cancel_releases_driver_capacity():
    driver_repository = InMemoryDriverRepository()
    ride_repository = InMemoryRideRepository()
    matching_service = InMemoryMatchingService(driver_repository)
    service = RideService(ride_repository, driver_repository, matching_service)

    driver = DriverProfile(
        user_id=uuid4(),
        vehicle_type=VehicleType.HATCHBACK,
        latitude=12.9700,
        longitude=77.5900,
        is_available=True,
    )
    driver_repository.add(driver)

    ride = service.create_ride(
        rider_id=uuid4(),
        pickup=Coordinate(12.9700, 77.5900),
        destination=Coordinate(12.9800, 77.6000),
        requested_vehicle_type=VehicleType.HATCHBACK,
    )

    cancelled = service.cancel_ride(ride.id)
    assert cancelled.status is RideStatus.CANCELLED
    assert driver_repository.get_by_user_id(driver.user_id).is_available is True


def test_ride_completion_sets_final_status():
    driver_repository = InMemoryDriverRepository()
    ride_repository = InMemoryRideRepository()
    matching_service = InMemoryMatchingService(driver_repository)
    service = RideService(ride_repository, driver_repository, matching_service)

    driver = DriverProfile(
        user_id=uuid4(),
        vehicle_type=VehicleType.SEDAN,
        latitude=12.9700,
        longitude=77.5900,
        is_available=True,
    )
    driver_repository.add(driver)

    ride = service.create_ride(
        rider_id=uuid4(),
        pickup=Coordinate(12.9700, 77.5900),
        destination=Coordinate(12.9810, 77.6010),
        requested_vehicle_type=VehicleType.SEDAN,
    )

    completed = service.complete_ride(ride.id)
    assert completed.status is RideStatus.COMPLETED
    assert completed.final_fare is not None
    assert driver_repository.get_by_user_id(driver.user_id).is_available is True


def test_hatchback_request_upgraded_to_sedan_keeps_hatchback_fare():
    driver_repository = InMemoryDriverRepository()
    ride_repository = InMemoryRideRepository()
    service = RideService(
        ride_repository,
        driver_repository,
        InMemoryMatchingService(driver_repository),
    )
    driver = DriverProfile(
        user_id=uuid4(),
        vehicle_type=VehicleType.SEDAN,
        latitude=12.9700,
        longitude=77.5900,
    )
    driver_repository.add(driver)

    pickup = Coordinate(12.9700, 77.5900)
    destination = Coordinate(13.0500, 77.5900)
    ride = service.create_ride(
        rider_id=uuid4(),
        pickup=pickup,
        destination=destination,
        requested_vehicle_type=VehicleType.HATCHBACK,
    )

    hatchback_fare = PricingService.calculate_fare_for_trip(pickup, destination, VehicleType.HATCHBACK)
    sedan_fare = PricingService.calculate_fare_for_trip(pickup, destination, VehicleType.SEDAN)
    assert ride.assigned_vehicle_type is VehicleType.SEDAN
    assert ride.final_fare == hatchback_fare
    assert ride.final_fare < sedan_fare


def test_invalid_coupon_does_not_claim_driver():
    driver_repository = InMemoryDriverRepository()
    ride_repository = InMemoryRideRepository()
    coupon_service = CouponService(InMemoryCouponRepository())
    service = RideService(
        ride_repository,
        driver_repository,
        InMemoryMatchingService(driver_repository),
        coupon_service,
    )
    driver = DriverProfile(
        user_id=uuid4(),
        vehicle_type=VehicleType.SEDAN,
        latitude=12.9700,
        longitude=77.5900,
    )
    driver_repository.add(driver)

    rider_id = uuid4()
    with pytest.raises(InvalidCouponError):
        service.create_ride(
            rider_id=rider_id,
            pickup=Coordinate(12.9700, 77.5900),
            destination=Coordinate(12.9800, 77.6000),
            requested_vehicle_type=VehicleType.SEDAN,
            coupon_code="NOT-VALID",
        )

    assert driver_repository.get_by_user_id(driver.user_id).is_available is True
    assert ride_repository.list_by_rider(rider_id) == []
