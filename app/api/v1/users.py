from fastapi import APIRouter, Depends, HTTPException, status

from app.repositories.memory.user_repository import InMemoryUserRepository
from app.schemas.user import UserCreateRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service() -> UserService:
    from app.main import app

    if not hasattr(app.state, "user_repository"):
        app.state.user_repository = InMemoryUserRepository()
    if not hasattr(app.state, "user_service"):
        app.state.user_service = UserService(app.state.user_repository)
    return app.state.user_service


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreateRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    try:
        user = service.register_user(name=payload.name, phone=payload.phone, roles=payload.roles)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserResponse(
        id=user.id,
        name=user.name,
        phone=user.phone,
        roles=user.roles,
        created_at=user.created_at,
    )
