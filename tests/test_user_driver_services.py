import pytest

from app.domain.enums import VehicleType
from app.repositories.memory.driver_repository import InMemoryDriverRepository
from app.repositories.memory.user_repository import InMemoryUserRepository
from app.services.driver_service import DriverService
from app.services.user_service import UserService


@pytest.fixture()
def services():
    user_repository = InMemoryUserRepository()
    driver_repository = InMemoryDriverRepository()
    return UserService(user_repository), DriverService(user_repository, driver_repository)


def test_user_registration_creates_rider_profile(services):
    user_service, _ = services
    user = user_service.register_user(name="Alice", phone="9999999999", roles=["rider"])

    assert user.name == "Alice"
    assert user.phone == "9999999999"
    assert user.roles == ["rider"]


def test_driver_registration_and_location_update(services):
    user_service, driver_service = services
    user_service.register_user(name="Alice", phone="9999999999", roles=["rider"])

    profile = driver_service.register_driver(
        name="Bob",
        phone="8888888888",
        vehicle_type=VehicleType.SEDAN,
        latitude=12.9716,
        longitude=77.5946,
    )

    assert profile.vehicle_type is VehicleType.SEDAN
    assert profile.is_available is True

    updated = driver_service.update_driver_location(profile.user_id, 12.9800, 77.6000)
    assert updated.latitude == 12.98
    assert updated.longitude == 77.6


def test_invalid_driver_coordinates_are_rejected(services):
    _, driver_service = services

    with pytest.raises(ValueError):
        driver_service.register_driver(
            name="Bob",
            phone="8888888888",
            vehicle_type=VehicleType.HATCHBACK,
            latitude=91.0,
            longitude=77.5946,
        )


def test_api_user_and_driver_registration(client):
    user_response = client.post(
        "/api/v1/users",
        json={"name": "Alice", "phone": "9999999999", "roles": ["rider"]},
    )
    assert user_response.status_code == 201
    assert user_response.json()["phone"] == "9999999999"

    driver_response = client.post(
        "/api/v1/drivers",
        json={
            "name": "Bob",
            "phone": "8888888888",
            "vehicle_type": "SEDAN",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "rating": 4.9,
        },
    )
    assert driver_response.status_code == 201
    assert driver_response.json()["vehicle_type"] == "SEDAN"

    update_response = client.patch(
        f"/api/v1/drivers/{driver_response.json()['id']}/location",
        json={"latitude": 12.9800, "longitude": 77.6000},
    )
    assert update_response.status_code == 200
    assert update_response.json()["latitude"] == 12.98
