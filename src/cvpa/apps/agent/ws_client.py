# -*- coding: utf-8 -*-

import json
from asyncio import Event, get_running_loop, sleep
from http.client import HTTPConnection, HTTPSConnection
from typing import Final, Optional
from urllib.parse import urlparse

from websockets.asyncio.client import ClientConnection, connect

from cvpa.logging.loggers import agent_logger as logger

CONNECT_PATH_TEMPLATE: Final[str] = "/api/agents/{slug}/connect"
INITIAL_BACKOFF: Final[float] = 1.0
MAX_BACKOFF: Final[float] = 60.0


class AgentWebSocketClient:
    def __init__(self, uri: str, slug: str, token: str) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._stop_event = Event()
        self._ws: Optional[ClientConnection] = None

    def _sync_request_ticket(self) -> str:
        parsed = urlparse(self._uri)
        path = CONNECT_PATH_TEMPLATE.format(slug=self._slug)
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

        conn: HTTPConnection
        if parsed.scheme == "https":
            conn = HTTPSConnection(parsed.netloc)
        else:
            conn = HTTPConnection(parsed.netloc)

        try:
            conn.request("POST", path, body="", headers=headers)
            resp = conn.getresponse()
            if resp.status != 200:
                body = resp.read().decode(errors="replace")
                raise RuntimeError(f"Ticket request failed ({resp.status}): {body}")
            data = json.loads(resp.read())
            return data["url"]
        finally:
            conn.close()

    async def _request_ticket(self) -> str:
        loop = get_running_loop()
        return await loop.run_in_executor(None, self._sync_request_ticket)

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
