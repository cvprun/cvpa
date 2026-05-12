# -*- coding: utf-8 -*-

from cvpa.logging.loggers import agent_logger as logger
from cvpa.ws.connection import AgentConnection


class AgentClient:
    def __init__(
        self,
        uri: str,
        slug: str,
        token: str,
        *,
        agent_version: str = "",
    ) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._connection = AgentConnection(
            uri=uri,
            slug=slug,
            token=token,
            logger=logger,
            agent_version=agent_version,
        )

    @property
    def connection(self) -> AgentConnection:
        return self._connection

    async def start(self) -> None:
        await self._connection.start()

    async def stop(self) -> None:
        await self._connection.stop()
