# -*- coding: utf-8 -*-

from asyncio import Event
from logging import Logger, getLogger
from typing import Any, AsyncIterator, Awaitable, Callable, Optional

import grpc.aio

from cvpa.protos.service_pb2 import Empty, Envelope, Pat, Pit
from cvpa.protos.service_pb2_grpc import (
    ManagedServiceServicer,
    add_ManagedServiceServicer_to_server,
)

OnEnvelopeCallback = Callable[[Envelope], Awaitable[None]]


class _Servicer(ManagedServiceServicer):
    def __init__(
        self,
        on_envelope: OnEnvelopeCallback,
        stop_event: Event,
        logger: Logger,
    ) -> None:
        self._on_envelope = on_envelope
        self._stop_event = stop_event
        self._logger = logger
        self._outbox: list[Envelope] = []
        self._outbox_event = Event()

    def enqueue(self, envelope: Envelope) -> None:
        self._outbox.append(envelope)
        self._outbox_event.set()

    async def Channel(
        self,
        request_iterator: AsyncIterator[Envelope],
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> AsyncIterator[Envelope]:
        async def _read() -> None:
            async for envelope in request_iterator:
                await self._on_envelope(envelope)

        import asyncio

        read_task = asyncio.create_task(_read())
        try:
            while not self._stop_event.is_set():
                await self._outbox_event.wait()
                self._outbox_event.clear()
                while self._outbox:
                    yield self._outbox.pop(0)
        finally:
            read_task.cancel()

    async def Heartbeat(
        self,
        request: Pit,
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> Pat:
        return Pat(ok=True)

    async def Shutdown(
        self,
        request: Empty,
        context: grpc.aio.ServicerContext[Any, Any],
    ) -> Empty:
        self._logger.info("Shutdown request received")
        self._stop_event.set()
        self._outbox_event.set()
        return Empty()


class ServiceServer:
    def __init__(
        self,
        socket_path: str,
        *,
        on_envelope: OnEnvelopeCallback,
        logger: Optional[Logger] = None,
    ) -> None:
        self._socket_path = socket_path
        self._stop_event = Event()
        self._logger = logger or getLogger(__name__)
        self._servicer = _Servicer(on_envelope, self._stop_event, self._logger)
        self._server: Optional[grpc.aio.Server] = None

    async def send(self, envelope: Envelope) -> None:
        self._servicer.enqueue(envelope)

    async def serve(self) -> None:
        self._server = grpc.aio.server()
        add_ManagedServiceServicer_to_server(self._servicer, self._server)
        self._server.add_insecure_port(f"unix://{self._socket_path}")
        await self._server.start()
        self._logger.info(f"gRPC server listening on unix://{self._socket_path}")
        await self._stop_event.wait()
        await self._server.stop(grace=5.0)
        self._logger.info("gRPC server stopped")
