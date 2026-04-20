# -*- coding: utf-8 -*-

from cvpa.logging.loggers import agent_logger as logger
from cvpa.service.manager import ServiceManager
from cvpa.ws.client import AgentConnection


class AgentClient:
    def __init__(
        self,
        uri: str,
        slug: str,
        token: str,
        *,
        legacy_protocol: bool = False,
        agent_version: str = "",
    ) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._services = ServiceManager(logger=logger)
        self._connection = AgentConnection(
            uri=uri,
            slug=slug,
            token=token,
            logger=logger,
            legacy_protocol=legacy_protocol,
            agent_version=agent_version,
            on_active=self._services.start_all,
            on_deactive=self._services.stop_all,
        )

    @property
    def services(self) -> ServiceManager:
        return self._services

    @property
    def connection(self) -> AgentConnection:
        return self._connection

    async def start(self) -> None:
        await self._connection.start()

    async def stop(self) -> None:
        await self._connection.stop()
        await self._services.stop_all()
