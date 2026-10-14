import threading

import pytest

from app.core.exceptions import NoDriverAvailableError
from app.domain.enums import VehicleType
from app.domain.models import Coordinate, DriverProfile
from app.repositories.memory.driver_repository import InMemoryDriverRepository
from app.services.matching_service import InMemoryMatchingService


def _make_service(radius_km: float = 5.0):
    repository = InMemoryDriverRepository()
    service = InMemoryMatchingService(repository, radius_km=radius_km)
    return repository, service


def test_nearby_driver_matching_prefers_exact_vehicle_type():
    repository, service = _make_service()
    near_hatchback = repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.HATCHBACK,
            latitude=12.9716,
            longitude=77.5946,
            is_available=True,
        )
    )
    repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.SEDAN,
            latitude=12.9750,
            longitude=77.5980,
            is_available=True,
        )
    )

    matched = service.claim_driver_for_ride(Coordinate(12.9700, 77.5900), VehicleType.HATCHBACK)
    assert matched.user_id == near_hatchback.user_id
    assert repository.get_by_user_id(near_hatchback.user_id).is_available is False


def test_drivers_outside_radius_are_rejected():
    repository, service = _make_service(radius_km=1.0)
    repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.SEDAN,
            latitude=12.9916,
            longitude=77.5946,
            is_available=True,
        )
    )

    with pytest.raises(NoDriverAvailableError):
        service.claim_driver_for_ride(Coordinate(12.9716, 77.5946), VehicleType.SEDAN, radius_km=1.0)


def test_unavailable_drivers_are_skipped():
    repository, service = _make_service()
    driver = repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.SEDAN,
            latitude=12.9716,
            longitude=77.5946,
            is_available=False,
        )
    )

    with pytest.raises(NoDriverAvailableError):
        service.claim_driver_for_ride(Coordinate(12.9700, 77.5900), VehicleType.SEDAN)
    assert repository.get_by_user_id(driver.user_id).is_available is False


def test_hatchback_requests_fall_back_to_sedan_upgrade():
    repository, service = _make_service()
    sedan_driver = repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.SEDAN,
            latitude=12.9716,
            longitude=77.5946,
            is_available=True,
        )
    )

    matched = service.claim_driver_for_ride(Coordinate(12.9700, 77.5900), VehicleType.HATCHBACK)
    assert matched.user_id == sedan_driver.user_id
    assert matched.vehicle_type is VehicleType.SEDAN


def test_no_driver_available_when_nothing_matches():
    repository, service = _make_service(radius_km=2.0)
    repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.SEDAN,
            latitude=13.2000,
            longitude=77.7000,
            is_available=True,
        )
    )

    with pytest.raises(NoDriverAvailableError):
        service.claim_driver_for_ride(Coordinate(12.9716, 77.5946), VehicleType.SEDAN, radius_km=2.0)


def test_competing_claims_do_not_assign_the_same_driver_twice():
    repository, service = _make_service(radius_km=10.0)
    driver = repository.add(
        DriverProfile(
            user_id=__import__("uuid").uuid4(),
            vehicle_type=VehicleType.SEDAN,
            latitude=12.9716,
            longitude=77.5946,
            is_available=True,
        )
    )

    results = []
    errors = []

    def attempt_booking():
        try:
            results.append(service.claim_driver_for_ride(Coordinate(12.9700, 77.5900), VehicleType.SEDAN))
        except Exception as exc:  # pragma: no cover - exercised for race behavior
            errors.append(exc)

    threads = [threading.Thread(target=attempt_booking) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert len(results) == 1
    assert results[0].user_id == driver.user_id
    assert len(errors) == 1
    assert isinstance(errors[0], NoDriverAvailableError)
