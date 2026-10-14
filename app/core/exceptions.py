class DomainError(Exception):
    """Base exception for domain-level validation and business logic errors."""


class NoDriverAvailableError(DomainError):
    pass


class RideNotFoundError(DomainError):
    pass


class RideAlreadyCompletedError(DomainError):
    pass


class RideNotActiveError(DomainError):
    pass


class InvalidCouponError(DomainError):
    pass
