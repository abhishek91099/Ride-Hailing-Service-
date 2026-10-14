from enum import Enum


class VehicleType(str, Enum):
    SEDAN = "SEDAN"
    HATCHBACK = "HATCHBACK"


class RideStatus(str, Enum):
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
