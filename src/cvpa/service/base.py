# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, Awaitable, Callable

OnMessageCallback = Callable[[Any], Awaitable[None]]


class ManagedService(ABC):
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @abstractmethod
    async def start(self) -> None: ...  # nocov

    @abstractmethod
    async def stop(self) -> None: ...  # nocov

    @abstractmethod
    async def send(self, data: dict) -> None: ...  # nocov

    @property
    @abstractmethod
    def is_alive(self) -> bool: ...  # nocov
