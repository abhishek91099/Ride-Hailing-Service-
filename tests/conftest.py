import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.repositories.memory.coupon_repository import InMemoryCouponRepository
from app.repositories.memory.driver_repository import InMemoryDriverRepository
from app.repositories.memory.ride_repository import InMemoryRideRepository
from app.repositories.memory.user_repository import InMemoryUserRepository
from app.services.coupon_service import CouponService
from app.services.driver_service import DriverService
from app.services.matching_service import InMemoryMatchingService
from app.services.ride_service import RideService
from app.services.user_service import UserService


@pytest.fixture()
def client():
    app.state.user_repository = InMemoryUserRepository()
    app.state.driver_repository = InMemoryDriverRepository()
    app.state.ride_repository = InMemoryRideRepository()
    app.state.coupon_repository = InMemoryCouponRepository()
    app.state.user_service = UserService(app.state.user_repository)
    app.state.driver_service = DriverService(app.state.user_repository, app.state.driver_repository)
    app.state.coupon_service = CouponService(app.state.coupon_repository)
    app.state.matching_service = InMemoryMatchingService(app.state.driver_repository)
    app.state.ride_service = RideService(
        app.state.ride_repository,
        app.state.driver_repository,
        app.state.matching_service,
        app.state.coupon_service,
    )
    with TestClient(app) as test_client:
        yield test_client
