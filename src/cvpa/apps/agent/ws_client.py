# -*- coding: utf-8 -*-

from asyncio import Event, get_running_loop, sleep
from typing import Final, Optional

from websockets.asyncio.client import ClientConnection, connect

from cvpa.client.ticket import request_ticket
from cvpa.logging.loggers import agent_logger as logger

INITIAL_BACKOFF: Final[float] = 1.0
MAX_BACKOFF: Final[float] = 60.0


class AgentWebSocketClient:
    def __init__(self, uri: str, slug: str, token: str) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._stop_event = Event()
        self._ws: Optional[ClientConnection] = None

    async def _request_ticket(self) -> str:
        loop = get_running_loop()
        return await loop.run_in_executor(
            None, request_ticket, self._uri, self._slug, self._token
        )

    async def _connect(self) -> None:
        ws_url = await self._request_ticket()
        logger.info(f"Connecting to WebSocket: {ws_url}")
        self._ws = await connect(ws_url)
        logger.info("WebSocket connected")

    async def _listen(self) -> None:
        assert self._ws is not None
        async for message in self._ws:
            if isinstance(message, bytes):
                logger.debug(f"Received: {message!r}")
            else:
                logger.debug(f"Received: {message}")

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
                logger.warning(f"Connection lost: {e}, reconnecting in {backoff}s")
                await sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)

    async def stop(self) -> None:
        self._stop_event.set()
        if self._ws is not None:
            await self._ws.close()
            self._ws = None
