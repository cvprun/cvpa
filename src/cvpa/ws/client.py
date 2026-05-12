# -*- coding: utf-8 -*-

import json
from asyncio import Event
from logging import Logger
from typing import Any, Awaitable, Callable, Dict, Optional, Union

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

OnMessageCallback = Callable[[Union[str, bytes]], Awaitable[None]]
GetUrlCallback = Callable[[], Awaitable[str]]


class WebSocketClient:
    """저수준 단일 연결 WS 클라이언트.

    재연결 루프는 보유하지 않는다. 상위 관리자(`AgentConnection`)가 주도한다.
    """

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

    @property
    def ws(self) -> Optional[ClientConnection]:
        return self._ws

    async def _connect(self) -> None:
        ws_url = await self._get_url()
        if self._logger:
            self._logger.info(f"Connecting to WebSocket: {ws_url}")
        self._ws = await connect(ws_url)
        if self._logger:
            self._logger.info("WebSocket connected")

    async def send(self, data: Union[str, bytes]) -> None:
        assert self._ws is not None
        await self._ws.send(data)

    async def send_json(self, obj: Dict[str, Any]) -> None:
        await self.send(json.dumps(obj))

    async def _listen(self) -> None:
        assert self._ws is not None
        async for message in self._ws:
            await self._on_message(message)

    async def start(self) -> None:
        """1회 연결 + 수신 루프. 연결이 닫히면 반환."""
        await self._connect()
        try:
            await self._listen()
        except ConnectionClosed:
            return

    async def close(self, code: int = 1000, reason: str = "") -> None:
        if self._ws is not None:
            try:
                await self._ws.close(code=code, reason=reason)
            except Exception:  # noqa: BLE001
                pass
            self._ws = None

    async def stop(self) -> None:
        self._stop_event.set()
        await self.close()
