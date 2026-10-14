from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Settings:
    app_name: str = "Ride Hailing Backend"
    api_v1_prefix: str = "/api/v1"
    search_radius_km: float = 5.0
    minimum_fare: Decimal = Decimal("50.00")
    pricing_tier_limits_km: tuple[Decimal, ...] = (Decimal("2"), Decimal("5"))
    sedan_rates_per_km: tuple[Decimal, ...] = (
        Decimal("10"),
        Decimal("8"),
        Decimal("5"),
    )
    hatchback_rates_per_km: tuple[Decimal, ...] = (
        Decimal("8"),
        Decimal("6"),
        Decimal("4"),
    )


settings = Settings()
