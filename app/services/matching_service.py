from __future__ import annotations

import math
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings
from app.core.exceptions import NoDriverAvailableError
from app.domain.enums import VehicleType
from app.domain.models import Coordinate, DriverProfile
from app.repositories.interfaces import DriverRepository


@dataclass(frozen=True)
class DriverCandidate:
    driver: DriverProfile
    distance_km: float


class DriverMatchingService(ABC):
    @abstractmethod
    def claim_driver_for_ride(
        self,
        pickup: Coordinate,
        requested_vehicle_type: VehicleType,
        radius_km: float | None = None,
    ) -> DriverProfile:
        raise NotImplementedError


class InMemoryMatchingService(DriverMatchingService):
    """Process-local matching service.

    The RLock protects concurrent access within a single Python process. This is enough for
    in-process race safety, but it is not sufficient across multiple worker processes; for that,
    a distributed lock or database-backed claim would be needed.
    """

    def __init__(self, driver_repository: DriverRepository, radius_km: float | None = None) -> None:
        self.driver_repository = driver_repository
        self.radius_km = radius_km if radius_km is not None else settings.search_radius_km
        self._lock = threading.RLock()

    @staticmethod
    def haversine_km(start: Coordinate, end: Coordinate) -> float:
        earth_radius_km = 6371.0
        latitude_delta = math.radians(end.latitude - start.latitude)
        longitude_delta = math.radians(end.longitude - start.longitude)
        start_latitude = math.radians(start.latitude)
        end_latitude = math.radians(end.latitude)

        a = (
            math.sin(latitude_delta / 2) ** 2
            + math.cos(start_latitude) * math.cos(end_latitude) * math.sin(longitude_delta / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return earth_radius_km * c

    def _ordered_candidates_for(
        self,
        pickup: Coordinate,
        requested_vehicle_type: VehicleType,
        radius_km: float,
    ) -> list[DriverCandidate]:
        candidates: list[DriverCandidate] = []

        for profile in self.driver_repository.list_all():
            if not profile.is_available:
                continue

            distance_km = self.haversine_km(pickup, Coordinate(profile.latitude, profile.longitude))
            if distance_km > radius_km:
                continue

            candidates.append(DriverCandidate(driver=profile, distance_km=distance_km))

        exact_match = [candidate for candidate in candidates if candidate.driver.vehicle_type == requested_vehicle_type]
        exact_match.sort(key=lambda candidate: candidate.distance_km)

        if requested_vehicle_type is VehicleType.HATCHBACK:
            sedan_fallback = [
                candidate for candidate in candidates if candidate.driver.vehicle_type == VehicleType.SEDAN
            ]
            sedan_fallback.sort(key=lambda candidate: candidate.distance_km)
            ordered = exact_match or sedan_fallback
        else:
            ordered = exact_match

        return ordered

    def claim_driver_for_ride(
        self,
        pickup: Coordinate,
        requested_vehicle_type: VehicleType,
        radius_km: float | None = None,
    ) -> DriverProfile:
        search_radius = radius_km if radius_km is not None else self.radius_km

        with self._lock:
            candidates = self._ordered_candidates_for(pickup, requested_vehicle_type, search_radius)
            for candidate in candidates:
                current_profile = self.driver_repository.get_by_user_id(candidate.driver.user_id)
                if current_profile is None or not current_profile.is_available:
                    continue

                claimed_profile = self.driver_repository.set_availability(current_profile.user_id, False)
                if claimed_profile.is_available is False:
                    return claimed_profile

            raise NoDriverAvailableError(
                "No eligible driver available within the configured search radius for the requested vehicle type."
            )
