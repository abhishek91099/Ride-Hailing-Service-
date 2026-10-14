from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.core.exceptions import RideAlreadyCompletedError, RideNotActiveError, RideNotFoundError
from app.domain.enums import RideStatus
from app.domain.models import Coordinate, Ride
from app.repositories.interfaces import DriverRepository, RideRepository
from app.services.coupon_service import CouponService
from app.services.matching_service import DriverMatchingService
from app.services.pricing_service import PricingService


class RideService:
    def __init__(
        self,
        ride_repository: RideRepository,
        driver_repository: DriverRepository,
        matching_service: DriverMatchingService,
        coupon_service: CouponService | None = None,
    ) -> None:
        self.ride_repository = ride_repository
        self.driver_repository = driver_repository
        self.matching_service = matching_service
        self.coupon_service = coupon_service

    def get_ride(self, ride_id: UUID) -> Ride | None:
        return self.ride_repository.get_by_id(ride_id)

    def list_rides_for_rider(self, rider_id: UUID) -> list[Ride]:
        return self.ride_repository.list_by_rider(rider_id)

    def list_rides_for_driver(self, driver_id: UUID) -> list[Ride]:
        return self.ride_repository.list_by_driver(driver_id)

    def _calculate_fare(
        self,
        pickup: Coordinate,
        destination: Coordinate,
        requested_vehicle_type,
        coupon_code: str | None,
    ) -> Decimal:
        # Fare by the requested class so a free upgrade does not increase the price.
        fare = PricingService.calculate_fare_for_trip(
            pickup,
            destination,
            requested_vehicle_type,
        )
        if coupon_code:
            if self.coupon_service is None:
                raise ValueError("Coupon service is not configured")
            fare = self.coupon_service.apply_coupon_to_fare(fare, coupon_code)
        return fare.quantize(Decimal("0.01"))

    def _calculate_final_fare(self, ride: Ride) -> Decimal:
        return self._calculate_fare(
            ride.pickup,
            ride.destination,
            ride.requested_vehicle_type,
            ride.coupon_code,
        )

    def create_ride(
        self,
        *,
        rider_id: UUID,
        pickup: Coordinate,
        destination: Coordinate,
        requested_vehicle_type,
        coupon_code: str | None = None,
    ) -> Ride:
        if rider_id is None:
            raise ValueError("Rider id is required to create a ride")

        pickup_coordinate = Coordinate(latitude=pickup.latitude, longitude=pickup.longitude)
        destination_coordinate = Coordinate(latitude=destination.latitude, longitude=destination.longitude)

        normalized_coupon_code = coupon_code.strip().upper() if coupon_code else None
        final_fare = self._calculate_fare(
            pickup_coordinate,
            destination_coordinate,
            requested_vehicle_type,
            normalized_coupon_code,
        )

        driver = self.matching_service.claim_driver_for_ride(pickup_coordinate, requested_vehicle_type)
        ride = Ride(
            rider_id=rider_id,
            driver_id=driver.user_id,
            pickup=pickup_coordinate,
            destination=destination_coordinate,
            requested_vehicle_type=requested_vehicle_type,
            assigned_vehicle_type=driver.vehicle_type,
            status=RideStatus.ONGOING,
            coupon_code=normalized_coupon_code,
            final_fare=final_fare,
        )
        return self.ride_repository.add(ride)

    def complete_ride(self, ride_id: UUID) -> Ride:
        ride = self.ride_repository.get_by_id(ride_id)
        if ride is None:
            raise RideNotFoundError(f"Ride {ride_id} not found")
        if ride.status is RideStatus.COMPLETED:
            raise RideAlreadyCompletedError(f"Ride {ride_id} is already completed")
        if ride.status is RideStatus.CANCELLED:
            raise RideNotActiveError(f"Ride {ride_id} has been cancelled and cannot be completed")

        ride.status = RideStatus.COMPLETED
        ride.completed_at = datetime.now(timezone.utc)
        if ride.final_fare is None:
            ride.final_fare = self._calculate_final_fare(ride)
        if ride.driver_id is not None:
            self.driver_repository.set_availability(ride.driver_id, True)
        return self.ride_repository.update(ride)

    def cancel_ride(self, ride_id: UUID) -> Ride:
        ride = self.ride_repository.get_by_id(ride_id)
        if ride is None:
            raise RideNotFoundError(f"Ride {ride_id} not found")
        if ride.status is RideStatus.COMPLETED:
            raise RideAlreadyCompletedError(f"Ride {ride_id} is already completed")
        if ride.status is RideStatus.CANCELLED:
            return ride

        ride.status = RideStatus.CANCELLED
        if ride.driver_id is not None:
            self.driver_repository.set_availability(ride.driver_id, True)
        return self.ride_repository.update(ride)
