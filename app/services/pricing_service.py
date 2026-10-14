from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP

from app.core.config import settings
from app.domain.enums import VehicleType
from app.domain.models import Coordinate


class PricingService:
    """Calculates trip pricing using marginal tiered fare logic.

    Assumptions:
    - Distance is the straight-line Haversine distance between pickup and destination.
    - Rates are applied per marginal tier, not as one flat rate for the entire trip.
    - A minimum fare is enforced before any coupon discount.
    - Hatchback rates are lower than Sedan rates; see core settings for the assumption.
    """

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

    @staticmethod
    def _as_decimal(value: Decimal | int | float) -> Decimal:
        return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def calculate_trip_distance_km(cls, pickup: Coordinate, destination: Coordinate) -> Decimal:
        return cls._as_decimal(cls.haversine_km(pickup, destination))

    @classmethod
    def calculate_fare_for_distance(
        cls,
        distance_km: Decimal | int | float,
        vehicle_type: VehicleType,
        pricing_settings=settings,
    ) -> Decimal:
        distance = Decimal(str(distance_km))
        if distance < 0:
            raise ValueError("distance must not be negative")

        if vehicle_type is VehicleType.SEDAN:
            rates = pricing_settings.sedan_rates_per_km
        elif vehicle_type is VehicleType.HATCHBACK:
            rates = pricing_settings.hatchback_rates_per_km
        else:
            raise ValueError(f"Unsupported vehicle type for pricing: {vehicle_type}")

        tier_limits = pricing_settings.pricing_tier_limits_km
        if len(rates) != len(tier_limits) + 1:
            raise ValueError("each pricing schedule needs one more rate than there are tier limits")
        if any(limit <= 0 for limit in tier_limits) or tuple(sorted(set(tier_limits))) != tier_limits:
            raise ValueError("pricing tier limits must be positive and strictly increasing")
        if any(rate < 0 for rate in rates):
            raise ValueError("pricing rates must not be negative")

        total = Decimal("0")
        remaining_distance = distance
        previous_limit = Decimal("0")
        for tier_limit, rate in zip(tier_limits, rates):
            tier_distance = min(remaining_distance, tier_limit - previous_limit)
            total += tier_distance * rate
            remaining_distance -= tier_distance
            previous_limit = tier_limit
            if remaining_distance <= 0:
                break
        if remaining_distance > 0:
            total += remaining_distance * rates[-1]

        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def calculate_fare_for_trip(
        cls,
        pickup: Coordinate,
        destination: Coordinate,
        vehicle_type: VehicleType,
        pricing_settings=settings,
    ) -> Decimal:
        distance_km = cls.calculate_trip_distance_km(pickup, destination)
        fare = cls.calculate_fare_for_distance(distance_km, vehicle_type, pricing_settings)
        minimum_fare = pricing_settings.minimum_fare
        if fare < minimum_fare:
            return minimum_fare.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return fare

    @classmethod
    def apply_coupon_discount(cls, fare: Decimal, discount_percentage: Decimal) -> Decimal:
        if discount_percentage < 0 or discount_percentage > Decimal("100"):
            raise ValueError("discount percentage must be between 0 and 100")
        discount = (fare * discount_percentage) / Decimal("100")
        return (fare - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
