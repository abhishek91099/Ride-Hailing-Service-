from __future__ import annotations

import threading
from uuid import UUID

from app.domain.models import User
from app.repositories.interfaces import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}
        self._phone_index: dict[str, UUID] = {}
        self._lock = threading.RLock()

    def add(self, user: User) -> User:
        with self._lock:
            if user.phone in self._phone_index:
                raise ValueError(f"User with phone {user.phone} already exists")
            self._users[user.id] = user
            self._phone_index[user.phone] = user.id
            return user

    def get_by_id(self, user_id: UUID) -> User | None:
        with self._lock:
            return self._users.get(user_id)

    def get_by_phone(self, phone: str) -> User | None:
        with self._lock:
            user_id = self._phone_index.get(phone)
            if user_id is None:
                return None
            return self._users.get(user_id)

    def list(self) -> list[User]:
        with self._lock:
            return list(self._users.values())

    def clear(self) -> None:
        with self._lock:
            self._users.clear()
            self._phone_index.clear()
