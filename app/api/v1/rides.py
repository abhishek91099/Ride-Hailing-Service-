from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.exceptions import (
    InvalidCouponError,
    NoDriverAvailableError,
    RideAlreadyCompletedError,
    RideNotActiveError,
    RideNotFoundError,
)
from app.repositories.memory.coupon_repository import InMemoryCouponRepository
from app.repositories.memory.driver_repository import InMemoryDriverRepository
from app.repositories.memory.ride_repository import InMemoryRideRepository
from app.repositories.memory.user_repository import InMemoryUserRepository
from app.schemas.ride import RideCreateRequest, RideResponse
from app.services.coupon_service import CouponService
from app.services.matching_service import InMemoryMatchingService
from app.services.ride_service import RideService

router = APIRouter(prefix="/rides", tags=["rides"])


def get_ride_service() -> RideService:
    from app.main import app

    if not hasattr(app.state, "user_repository"):
        app.state.user_repository = InMemoryUserRepository()
    if not hasattr(app.state, "driver_repository"):
        app.state.driver_repository = InMemoryDriverRepository()
    if not hasattr(app.state, "ride_repository"):
        app.state.ride_repository = InMemoryRideRepository()
    if not hasattr(app.state, "coupon_repository"):
        app.state.coupon_repository = InMemoryCouponRepository()
    if not hasattr(app.state, "coupon_service"):
        app.state.coupon_service = CouponService(app.state.coupon_repository)
    if not hasattr(app.state, "matching_service"):
        app.state.matching_service = InMemoryMatchingService(app.state.driver_repository)
    if not hasattr(app.state, "ride_service"):
        app.state.ride_service = RideService(
            app.state.ride_repository,
            app.state.driver_repository,
            app.state.matching_service,
            app.state.coupon_service,
        )
    return app.state.ride_service


@router.get("/health")
async def rides_health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
async def create_ride(
    payload: RideCreateRequest,
    service: RideService = Depends(get_ride_service),
) -> RideResponse:
    try:
        ride = service.create_ride(
            rider_id=payload.rider_id,
            pickup=payload.pickup,
            destination=payload.destination,
            requested_vehicle_type=payload.requested_vehicle_type,
            coupon_code=payload.coupon_code,
        )
    except (ValueError, InvalidCouponError, NoDriverAvailableError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RideResponse(
        id=ride.id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        pickup={"latitude": ride.pickup.latitude, "longitude": ride.pickup.longitude},
        destination={"latitude": ride.destination.latitude, "longitude": ride.destination.longitude},
        requested_vehicle_type=ride.requested_vehicle_type,
        assigned_vehicle_type=ride.assigned_vehicle_type,
        status=ride.status,
        coupon_code=ride.coupon_code,
        final_fare=ride.final_fare,
        created_at=ride.created_at,
        completed_at=ride.completed_at,
    )


@router.get("/{ride_id}", response_model=RideResponse)
async def get_ride(
    ride_id: UUID,
    service: RideService = Depends(get_ride_service),
) -> RideResponse:
    ride = service.get_ride(ride_id)
    if ride is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")

    return RideResponse(
        id=ride.id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        pickup={"latitude": ride.pickup.latitude, "longitude": ride.pickup.longitude},
        destination={"latitude": ride.destination.latitude, "longitude": ride.destination.longitude},
        requested_vehicle_type=ride.requested_vehicle_type,
        assigned_vehicle_type=ride.assigned_vehicle_type,
        status=ride.status,
        coupon_code=ride.coupon_code,
        final_fare=ride.final_fare,
        created_at=ride.created_at,
        completed_at=ride.completed_at,
    )


@router.get("/users/{rider_id}", response_model=list[RideResponse])
async def list_rides_for_rider(
    rider_id: UUID,
    service: RideService = Depends(get_ride_service),
) -> list[RideResponse]:
    rides = service.list_rides_for_rider(rider_id)
    return [
        RideResponse(
            id=ride.id,
            rider_id=ride.rider_id,
            driver_id=ride.driver_id,
            pickup={"latitude": ride.pickup.latitude, "longitude": ride.pickup.longitude},
            destination={"latitude": ride.destination.latitude, "longitude": ride.destination.longitude},
            requested_vehicle_type=ride.requested_vehicle_type,
            assigned_vehicle_type=ride.assigned_vehicle_type,
            status=ride.status,
            coupon_code=ride.coupon_code,
            final_fare=ride.final_fare,
            created_at=ride.created_at,
            completed_at=ride.completed_at,
        )
        for ride in rides
    ]


@router.get("/drivers/{driver_id}", response_model=list[RideResponse])
async def list_rides_for_driver(
    driver_id: UUID,
    service: RideService = Depends(get_ride_service),
) -> list[RideResponse]:
    rides = service.list_rides_for_driver(driver_id)
    return [
        RideResponse(
            id=ride.id,
            rider_id=ride.rider_id,
            driver_id=ride.driver_id,
            pickup={"latitude": ride.pickup.latitude, "longitude": ride.pickup.longitude},
            destination={"latitude": ride.destination.latitude, "longitude": ride.destination.longitude},
            requested_vehicle_type=ride.requested_vehicle_type,
            assigned_vehicle_type=ride.assigned_vehicle_type,
            status=ride.status,
            coupon_code=ride.coupon_code,
            final_fare=ride.final_fare,
            created_at=ride.created_at,
            completed_at=ride.completed_at,
        )
        for ride in rides
    ]


@router.patch("/{ride_id}/complete", response_model=RideResponse)
async def complete_ride(
    ride_id: UUID,
    service: RideService = Depends(get_ride_service),
) -> RideResponse:
    try:
        ride = service.complete_ride(ride_id)
    except RideNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (RideAlreadyCompletedError, RideNotActiveError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RideResponse(
        id=ride.id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        pickup={"latitude": ride.pickup.latitude, "longitude": ride.pickup.longitude},
        destination={"latitude": ride.destination.latitude, "longitude": ride.destination.longitude},
        requested_vehicle_type=ride.requested_vehicle_type,
        assigned_vehicle_type=ride.assigned_vehicle_type,
        status=ride.status,
        coupon_code=ride.coupon_code,
        final_fare=ride.final_fare,
        created_at=ride.created_at,
        completed_at=ride.completed_at,
    )


@router.patch("/{ride_id}/cancel", response_model=RideResponse)
async def cancel_ride(
    ride_id: UUID,
    service: RideService = Depends(get_ride_service),
) -> RideResponse:
    try:
        ride = service.cancel_ride(ride_id)
    except RideNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RideAlreadyCompletedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return RideResponse(
        id=ride.id,
        rider_id=ride.rider_id,
        driver_id=ride.driver_id,
        pickup={"latitude": ride.pickup.latitude, "longitude": ride.pickup.longitude},
        destination={"latitude": ride.destination.latitude, "longitude": ride.destination.longitude},
        requested_vehicle_type=ride.requested_vehicle_type,
        assigned_vehicle_type=ride.assigned_vehicle_type,
        status=ride.status,
        coupon_code=ride.coupon_code,
        final_fare=ride.final_fare,
        created_at=ride.created_at,
        completed_at=ride.completed_at,
    )
