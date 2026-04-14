# -*- coding: utf-8 -*-

import asyncio
from logging import Logger, getLogger
from typing import Optional

from cvpa.service.base import OnMessageCallback
from cvpa.service.process import ProcessService


class ServiceManager:
    def __init__(self, *, logger: Optional[Logger] = None) -> None:
        self._logger = logger or getLogger(__name__)
        self._services: dict[str, ProcessService] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}

    def add(
        self,
        name: str,
        cmd: list[str],
        *,
        on_message: OnMessageCallback,
        auto_restart: bool = True,
    ) -> None:
        if name in self._services:
            raise ValueError(f"Service '{name}' already registered")
        self._services[name] = ProcessService(
            name,
            cmd,
            on_message=on_message,
            auto_restart=auto_restart,
            logger=self._logger,
        )

    async def start(self, name: str) -> None:
        svc = self._services[name]
        self._tasks[name] = asyncio.create_task(svc.start())

    async def start_all(self) -> None:
        for name in self._services:
            await self.start(name)

    async def stop(self, name: str) -> None:
        svc = self._services[name]
        await svc.stop()
        task = self._tasks.pop(name, None)
        if task is not None:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def stop_all(self) -> None:
        await asyncio.gather(
            *(self.stop(name) for name in list(self._services)),
            return_exceptions=True,
        )

    async def send(self, name: str, data: dict) -> None:
        svc = self._services[name]
        await svc.send(data)

    def list_services(self) -> dict[str, bool]:
        return {name: svc.is_alive for name, svc in self._services.items()}
