from __future__ import annotations

from decimal import Decimal

from app.core.exceptions import InvalidCouponError
from app.domain.models import Coupon
from app.repositories.interfaces import CouponRepository


class CouponService:
    def __init__(self, coupon_repository: CouponRepository) -> None:
        self.coupon_repository = coupon_repository

    def create_coupon(self, *, code: str, discount_percentage: Decimal, active: bool = True) -> Coupon:
        normalized_code = code.strip().upper()
        coupon = Coupon(code=normalized_code, discount_percentage=discount_percentage, active=active)
        return self.coupon_repository.add(coupon)

    def get_coupon(self, code: str) -> Coupon | None:
        return self.coupon_repository.get_by_code(code)

    def delete_coupon(self, code: str) -> bool:
        return self.coupon_repository.delete(code)

    def validate_coupon(self, code: str) -> Coupon:
        coupon = self.coupon_repository.get_by_code(code)
        if coupon is None or not coupon.active:
            raise InvalidCouponError("Coupon is invalid or inactive")
        return coupon

    def apply_coupon_to_fare(self, fare: Decimal, code: str) -> Decimal:
        coupon = self.validate_coupon(code)
        if coupon.discount_percentage < 0 or coupon.discount_percentage > Decimal("100"):
            raise InvalidCouponError("Coupon discount percentage is outside the valid range")
        discount = (fare * coupon.discount_percentage) / Decimal("100")
        return (fare - discount).quantize(Decimal("0.01"))
