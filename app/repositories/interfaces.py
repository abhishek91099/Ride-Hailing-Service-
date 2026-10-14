from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models import Coupon, DriverProfile, Ride, User


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_phone(self, phone: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[User]:
        raise NotImplementedError


class DriverRepository(ABC):
    @abstractmethod
    def add(self, profile: DriverProfile) -> DriverProfile:
        raise NotImplementedError

    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> DriverProfile | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, driver_id: UUID) -> DriverProfile | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[DriverProfile]:
        raise NotImplementedError

    @abstractmethod
    def update_location(self, driver_id: UUID, latitude: float, longitude: float) -> DriverProfile:
        raise NotImplementedError

    @abstractmethod
    def set_availability(self, driver_id: UUID, is_available: bool) -> DriverProfile:
        raise NotImplementedError


class RideRepository(ABC):
    @abstractmethod
    def add(self, ride: Ride) -> Ride:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, ride_id: UUID) -> Ride | None:
        raise NotImplementedError

    @abstractmethod
    def list_by_rider(self, rider_id: UUID) -> list[Ride]:
        raise NotImplementedError

    @abstractmethod
    def list_by_driver(self, driver_id: UUID) -> list[Ride]:
        raise NotImplementedError

    @abstractmethod
    def update(self, ride: Ride) -> Ride:
        raise NotImplementedError


class CouponRepository(ABC):
    @abstractmethod
    def add(self, coupon: Coupon) -> Coupon:
        raise NotImplementedError

    @abstractmethod
    def get_by_code(self, code: str) -> Coupon | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, code: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Coupon]:
        raise NotImplementedError
