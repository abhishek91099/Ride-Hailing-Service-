from __future__ import annotations

import threading
from uuid import UUID

from app.domain.models import DriverProfile
from app.repositories.interfaces import DriverRepository


class InMemoryDriverRepository(DriverRepository):
    def __init__(self) -> None:
        self._drivers: dict[UUID, DriverProfile] = {}
        self._by_user_id: dict[UUID, UUID] = {}
        self._lock = threading.RLock()

    def add(self, profile: DriverProfile) -> DriverProfile:
        with self._lock:
            self._drivers[profile.user_id] = profile
            self._by_user_id[profile.user_id] = profile.user_id
            return profile

    def get_by_user_id(self, user_id: UUID) -> DriverProfile | None:
        with self._lock:
            return self._drivers.get(user_id)

    def get_by_id(self, driver_id: UUID) -> DriverProfile | None:
        with self._lock:
            for profile in self._drivers.values():
                if profile.user_id == driver_id:
                    return profile
            return None

    def list_all(self) -> list[DriverProfile]:
        with self._lock:
            return list(self._drivers.values())

    def update_location(self, driver_id: UUID, latitude: float, longitude: float) -> DriverProfile:
        with self._lock:
            profile = self._drivers.get(driver_id)
            if profile is None:
                raise KeyError(f"Driver {driver_id} not found")
            profile.latitude = latitude
            profile.longitude = longitude
            return profile

    def set_availability(self, driver_id: UUID, is_available: bool) -> DriverProfile:
        with self._lock:
            profile = self._drivers.get(driver_id)
            if profile is None:
                raise KeyError(f"Driver {driver_id} not found")
            profile.is_available = is_available
            return profile

    def clear(self) -> None:
        with self._lock:
            self._drivers.clear()
            self._by_user_id.clear()
