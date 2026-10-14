from decimal import Decimal

import pytest

from app.core.config import Settings, settings
from app.domain.enums import VehicleType
from app.domain.models import Coordinate
from app.services.pricing_service import PricingService


def test_sedan_tier_pricing_uses_marginal_rates():
    fare = PricingService.calculate_fare_for_distance(10, VehicleType.SEDAN)
    assert fare == Decimal("69.00")


def test_hatchback_tier_pricing_uses_marginal_rates():
    fare = PricingService.calculate_fare_for_distance(10, VehicleType.HATCHBACK)
    assert fare == Decimal("54.00")


def test_minimum_fare_is_applied_before_coupon_discount():
    fare = PricingService.calculate_fare_for_trip(
        Coordinate(latitude=12.9716, longitude=77.5946),
        Coordinate(latitude=12.9720, longitude=77.5950),
        VehicleType.SEDAN,
    )
    assert fare >= settings.minimum_fare
    assert fare == settings.minimum_fare


def test_coupon_discount_applies_once_to_the_amount():
    discounted = PricingService.apply_coupon_discount(Decimal("100.00"), Decimal("10"))
    assert discounted == Decimal("90.00")


def test_discount_rejects_invalid_percentages():
    with pytest.raises(ValueError):
        PricingService.apply_coupon_discount(Decimal("100.00"), Decimal("-1"))

    with pytest.raises(ValueError):
        PricingService.apply_coupon_discount(Decimal("100.00"), Decimal("101"))


def test_pricing_schedule_is_configurable():
    custom_settings = Settings(
        minimum_fare=Decimal("1.00"),
        pricing_tier_limits_km=(Decimal("1"),),
        sedan_rates_per_km=(Decimal("2"), Decimal("3")),
        hatchback_rates_per_km=(Decimal("1"), Decimal("2")),
    )

    assert PricingService.calculate_fare_for_distance(
        3,
        VehicleType.SEDAN,
        pricing_settings=custom_settings,
    ) == Decimal("8.00")
