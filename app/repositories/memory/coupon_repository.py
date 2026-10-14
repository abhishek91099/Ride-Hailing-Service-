from __future__ import annotations

import threading

from app.domain.models import Coupon
from app.repositories.interfaces import CouponRepository


class InMemoryCouponRepository(CouponRepository):
    def __init__(self) -> None:
        self._coupons: dict[str, Coupon] = {}
        self._lock = threading.RLock()

    def add(self, coupon: Coupon) -> Coupon:
        with self._lock:
            self._coupons[coupon.code.upper()] = coupon
            return coupon

    def get_by_code(self, code: str) -> Coupon | None:
        with self._lock:
            return self._coupons.get(code.upper())

    def delete(self, code: str) -> bool:
        with self._lock:
            normalized = code.upper()
            if normalized not in self._coupons:
                return False
            del self._coupons[normalized]
            return True

    def list_all(self) -> list[Coupon]:
        with self._lock:
            return list(self._coupons.values())

    def clear(self) -> None:
        with self._lock:
            self._coupons.clear()
