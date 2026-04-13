# -*- coding: utf-8 -*-

from asyncio import Event, sleep
from logging import Logger
from typing import Awaitable, Callable, Final, Optional, Union

from websockets.asyncio.client import ClientConnection, connect

INITIAL_BACKOFF: Final[float] = 1.0
MAX_BACKOFF: Final[float] = 60.0

OnMessageCallback = Callable[[Union[str, bytes]], Awaitable[None]]
GetUrlCallback = Callable[[], Awaitable[str]]


class WebSocketClient:
    def __init__(
        self,
        get_url: GetUrlCallback,
        on_message: OnMessageCallback,
        *,
        logger: Optional[Logger] = None,
    ) -> None:
        self._get_url = get_url
        self._on_message = on_message
        self._logger = logger
        self._stop_event = Event()
        self._ws: Optional[ClientConnection] = None

    async def _connect(self) -> None:
        ws_url = await self._get_url()
        if self._logger:
            self._logger.info(f"Connecting to WebSocket: {ws_url}")
        self._ws = await connect(ws_url)
        if self._logger:
            self._logger.info("WebSocket connected")

    async def _listen(self) -> None:
        assert self._ws is not None
        async for message in self._ws:
            await self._on_message(message)

    async def start(self) -> None:
        backoff = INITIAL_BACKOFF
        while not self._stop_event.is_set():
            try:
                await self._connect()
                backoff = INITIAL_BACKOFF
                await self._listen()
            except Exception as e:
                if self._stop_event.is_set():
                    break
                if self._logger:
                    self._logger.warning(
                        f"Connection lost: {e}, reconnecting in {backoff}s"
                    )
                await sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)

    async def stop(self) -> None:
        self._stop_event.set()
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
