from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.memory.coupon_repository import InMemoryCouponRepository
from app.schemas.coupon import CouponCreateRequest, CouponResponse
from app.services.coupon_service import CouponService

router = APIRouter(prefix="/coupons", tags=["coupons"])


def get_coupon_service() -> CouponService:
    from app.main import app

    if not hasattr(app.state, "coupon_repository"):
        app.state.coupon_repository = InMemoryCouponRepository()
    if not hasattr(app.state, "coupon_service"):
        app.state.coupon_service = CouponService(app.state.coupon_repository)
    return app.state.coupon_service


@router.get("/health")
async def coupons_health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    payload: CouponCreateRequest,
    service: CouponService = Depends(get_coupon_service),
) -> CouponResponse:
    try:
        coupon = service.create_coupon(
            code=payload.code,
            discount_percentage=payload.discount_percentage,
            active=payload.active,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return CouponResponse(code=coupon.code, discount_percentage=coupon.discount_percentage, active=coupon.active)


@router.get("", response_model=list[CouponResponse])
async def list_coupons(service: CouponService = Depends(get_coupon_service)) -> list[CouponResponse]:
    return [
        CouponResponse(code=coupon.code, discount_percentage=coupon.discount_percentage, active=coupon.active)
        for coupon in service.coupon_repository.list_all()
    ]


@router.get("/{code}", response_model=CouponResponse)
async def get_coupon(code: str, service: CouponService = Depends(get_coupon_service)) -> CouponResponse:
    coupon = service.get_coupon(code)
    if coupon is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
    return CouponResponse(code=coupon.code, discount_percentage=coupon.discount_percentage, active=coupon.active)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(code: str, service: CouponService = Depends(get_coupon_service)) -> None:
    deleted = service.delete_coupon(code)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coupon not found")
