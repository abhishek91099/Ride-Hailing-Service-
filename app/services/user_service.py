from __future__ import annotations

from uuid import uuid4

from app.domain.models import User
from app.repositories.interfaces import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register_user(self, *, name: str, phone: str, roles: list[str] | None = None) -> User:
        normalized_roles = list(roles or ["rider"])
        user = User(id=uuid4(), name=name.strip(), phone=phone.strip(), roles=normalized_roles)
        return self.user_repository.add(user)

    def get_user(self, user_id) -> User | None:
        return self.user_repository.get_by_id(user_id)

    def get_user_by_phone(self, phone: str) -> User | None:
        return self.user_repository.get_by_phone(phone)
