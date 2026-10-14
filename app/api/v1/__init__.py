from .coupons import router as coupons_router
from .drivers import router as drivers_router
from .rides import router as rides_router
from .users import router as users_router

__all__ = [
    "coupons_router",
    "drivers_router",
    "rides_router",
    "users_router",
]
