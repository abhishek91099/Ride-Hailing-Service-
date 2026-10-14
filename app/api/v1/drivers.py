from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.enums import VehicleType
from app.repositories.memory.driver_repository import InMemoryDriverRepository
from app.repositories.memory.user_repository import InMemoryUserRepository
from app.schemas.driver import DriverCreateRequest, DriverLocationUpdate, DriverProfileResponse
from app.services.driver_service import DriverService
from app.services.user_service import UserService

router = APIRouter(prefix="/drivers", tags=["drivers"])


def get_driver_service() -> DriverService:
    from app.main import app

    if not hasattr(app.state, "user_repository"):
        app.state.user_repository = InMemoryUserRepository()
    if not hasattr(app.state, "driver_repository"):
        app.state.driver_repository = InMemoryDriverRepository()
    if not hasattr(app.state, "user_service"):
        app.state.user_service = UserService(app.state.user_repository)
    if not hasattr(app.state, "driver_service"):
        app.state.driver_service = DriverService(app.state.user_repository, app.state.driver_repository)
    return app.state.driver_service


@router.post("", response_model=DriverProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_driver(
    payload: DriverCreateRequest,
    service: DriverService = Depends(get_driver_service),
) -> DriverProfileResponse:
    try:
        profile = service.register_driver(
            name=payload.name,
            phone=payload.phone,
            vehicle_type=payload.vehicle_type,
            latitude=payload.latitude,
            longitude=payload.longitude,
            rating=payload.rating,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    user = service.user_repository.get_by_id(profile.user_id)
    return DriverProfileResponse(
        id=profile.user_id,
        name=user.name,
        phone=user.phone,
        vehicle_type=profile.vehicle_type,
        latitude=profile.latitude,
        longitude=profile.longitude,
        is_available=profile.is_available,
        rating=profile.rating,
        created_at=user.created_at,
    )


@router.patch("/{driver_id}/location", response_model=DriverProfileResponse)
async def update_driver_location(
    driver_id: UUID,
    payload: DriverLocationUpdate,
    service: DriverService = Depends(get_driver_service),
) -> DriverProfileResponse:
    try:
        profile = service.update_driver_location(driver_id, payload.latitude, payload.longitude)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    user = service.user_repository.get_by_id(profile.user_id)
    return DriverProfileResponse(
        id=profile.user_id,
        name=user.name,
        phone=user.phone,
        vehicle_type=profile.vehicle_type,
        latitude=profile.latitude,
        longitude=profile.longitude,
        is_available=profile.is_available,
        rating=profile.rating,
        created_at=user.created_at,
    )
