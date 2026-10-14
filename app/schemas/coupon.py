from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CouponCreateRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=30)
    discount_percentage: Decimal = Field(..., ge=0, le=100)
    active: bool = True


class CouponResponse(BaseModel):
    code: str
    discount_percentage: Decimal
    active: bool
