from decimal import Decimal

import pytest

from app.core.exceptions import InvalidCouponError
from app.domain.models import Coupon
from app.repositories.memory.coupon_repository import InMemoryCouponRepository
from app.services.coupon_service import CouponService


@pytest.fixture()
def coupon_service():
    return CouponService(InMemoryCouponRepository())


def test_coupon_creation_and_lookup(coupon_service):
    coupon = coupon_service.create_coupon(code="SAVE10", discount_percentage=Decimal("10"), active=True)

    assert coupon.code == "SAVE10"
    assert coupon_service.get_coupon("save10").code == "SAVE10"


def test_inactive_or_missing_coupon_is_rejected(coupon_service):
    with pytest.raises(InvalidCouponError):
        coupon_service.apply_coupon_to_fare(Decimal("100.00"), "MISSING")

    coupon_service.create_coupon(code="SAVE20", discount_percentage=Decimal("20"), active=False)
    with pytest.raises(InvalidCouponError):
        coupon_service.apply_coupon_to_fare(Decimal("100.00"), "SAVE20")


def test_coupon_delete_removes_it_from_storage(coupon_service):
    coupon_service.create_coupon(code="SAVE15", discount_percentage=Decimal("15"), active=True)
    assert coupon_service.delete_coupon("save15") is True
    assert coupon_service.get_coupon("SAVE15") is None


def test_coupon_discount_applies_once(coupon_service):
    coupon_service.create_coupon(code="SAVE50", discount_percentage=Decimal("50"), active=True)
    discounted = coupon_service.apply_coupon_to_fare(Decimal("100.00"), "SAVE50")
    assert discounted == Decimal("50.00")
