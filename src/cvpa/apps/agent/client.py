# -*- coding: utf-8 -*-

from asyncio import get_running_loop

from cvpa.client.ticket import request_ticket
from cvpa.logging.loggers import agent_logger as logger
from cvpa.ws.client import WebSocketClient
from cvpa.ws.handler import MessageDispatcher


class AgentClient:
    def __init__(self, uri: str, slug: str, token: str) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._dispatcher = MessageDispatcher(logger=logger)
        self._client = WebSocketClient(
            get_url=self._request_ticket,
            on_message=self._dispatcher,
            logger=logger,
        )

    async def _request_ticket(self) -> str:
        loop = get_running_loop()
        return await loop.run_in_executor(
            None, request_ticket, self._uri, self._slug, self._token
        )

    async def start(self) -> None:
        await self._client.start()

    async def stop(self) -> None:
        await self._client.stop()
