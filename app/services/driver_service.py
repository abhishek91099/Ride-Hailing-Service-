from __future__ import annotations

from uuid import uuid4

from app.domain.enums import VehicleType
from app.domain.models import Coordinate, DriverProfile, User
from app.repositories.interfaces import DriverRepository, UserRepository


class DriverService:
    def __init__(self, user_repository: UserRepository, driver_repository: DriverRepository) -> None:
        self.user_repository = user_repository
        self.driver_repository = driver_repository

    def register_driver(
        self,
        *,
        name: str,
        phone: str,
        vehicle_type: VehicleType,
        latitude: float,
        longitude: float,
        rating: float = 5.0,
    ) -> DriverProfile:
        Coordinate(latitude=latitude, longitude=longitude)
        user = self.user_repository.get_by_phone(phone)
        if user is None:
            user = User(id=uuid4(), name=name.strip(), phone=phone.strip(), roles=["driver"])
            self.user_repository.add(user)
        else:
            if "driver" not in user.roles:
                user.roles = sorted(set(user.roles + ["driver"]))

        profile = DriverProfile(
            user_id=user.id,
            vehicle_type=vehicle_type,
            latitude=latitude,
            longitude=longitude,
            is_available=True,
            rating=rating,
        )
        return self.driver_repository.add(profile)

    def update_driver_location(self, driver_id, latitude: float, longitude: float) -> DriverProfile:
        Coordinate(latitude=latitude, longitude=longitude)
        return self.driver_repository.update_location(driver_id, latitude, longitude)

    def get_driver(self, driver_id):
        return self.driver_repository.get_by_id(driver_id)

    def list_drivers(self) -> list[DriverProfile]:
        return self.driver_repository.list_all()
