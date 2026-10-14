from __future__ import annotations

import threading
from uuid import UUID

from app.domain.models import Ride
from app.repositories.interfaces import RideRepository


class InMemoryRideRepository(RideRepository):
    def __init__(self) -> None:
        self._rides: dict[UUID, Ride] = {}
        self._lock = threading.RLock()

    def add(self, ride: Ride) -> Ride:
        with self._lock:
            self._rides[ride.id] = ride
            return ride

    def get_by_id(self, ride_id: UUID) -> Ride | None:
        with self._lock:
            return self._rides.get(ride_id)

    def list_by_rider(self, rider_id: UUID) -> list[Ride]:
        with self._lock:
            return [ride for ride in self._rides.values() if ride.rider_id == rider_id]

    def list_by_driver(self, driver_id: UUID) -> list[Ride]:
        with self._lock:
            return [ride for ride in self._rides.values() if ride.driver_id == driver_id]

    def update(self, ride: Ride) -> Ride:
        with self._lock:
            self._rides[ride.id] = ride
            return ride

    def clear(self) -> None:
        with self._lock:
            self._rides.clear()
