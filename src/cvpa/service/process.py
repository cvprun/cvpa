# -*- coding: utf-8 -*-

import asyncio
from asyncio import Event, create_subprocess_exec, sleep
from asyncio.subprocess import Process
from logging import Logger, getLogger
from os import unlink
from pathlib import Path
from typing import Final, Optional
from uuid import uuid4

import grpc.aio

from cvpa.protos.service_pb2 import Empty, Envelope
from cvpa.protos.service_pb2_grpc import ManagedServiceStub
from cvpa.service.base import ManagedService, OnMessageCallback

INITIAL_BACKOFF: Final[float] = 1.0
MAX_BACKOFF: Final[float] = 60.0
SHUTDOWN_TIMEOUT: Final[float] = 5.0
SOCKET_WAIT_INTERVAL: Final[float] = 0.1
SOCKET_WAIT_TIMEOUT: Final[float] = 30.0


class ProcessService(ManagedService):
    def __init__(
        self,
        name: str,
        cmd: list[str],
        *,
        on_message: OnMessageCallback,
        auto_restart: bool = True,
        logger: Optional[Logger] = None,
    ) -> None:
        super().__init__(name)
        self._cmd = cmd
        self._on_message = on_message
        self._auto_restart = auto_restart
        self._logger = (logger or getLogger(__name__)).getChild(name)
        self._stop_event = Event()
        self._socket_path = f"/tmp/cvpa-{name}-{uuid4().hex[:8]}.sock"
        self._process: Optional[Process] = None
        self._channel: Optional[grpc.aio.Channel] = None
        self._stub: Optional[ManagedServiceStub] = None

    @property
    def socket_path(self) -> str:
        return self._socket_path

    @property
    def is_alive(self) -> bool:
        return self._process is not None and self._process.returncode is None

    async def _wait_for_socket(self) -> bool:
        elapsed = 0.0
        while elapsed < SOCKET_WAIT_TIMEOUT:
            if self._stop_event.is_set():
                return False
            if Path(self._socket_path).exists():
                return True
            await sleep(SOCKET_WAIT_INTERVAL)
            elapsed += SOCKET_WAIT_INTERVAL
        return False

    async def _spawn(self) -> None:
        cmd = self._cmd + [f"--grpc-socket={self._socket_path}"]
        self._logger.info(f"Spawning: {' '.join(cmd)}")
        self._process = await create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

    async def _connect(self) -> None:
        if not await self._wait_for_socket():
            raise RuntimeError(f"Socket not ready: {self._socket_path}")
        self._channel = grpc.aio.insecure_channel(f"unix://{self._socket_path}")
        self._stub = ManagedServiceStub(self._channel)
        self._logger.info("gRPC channel connected")

    async def _drain_stderr(self) -> None:
        assert self._process is not None
        assert self._process.stderr is not None
        async for line in self._process.stderr:
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                self._logger.debug(text)

    async def _run_channel(self) -> None:
        assert self._stub is not None
        call = self._stub.Channel(iter([]))  # type: ignore[arg-type]
        async for envelope in call:
            await self._on_message(envelope)

    async def start(self) -> None:
        backoff = INITIAL_BACKOFF
        while not self._stop_event.is_set():
            try:
                await self._spawn()
                await self._connect()
                backoff = INITIAL_BACKOFF

                stderr_task = asyncio.create_task(self._drain_stderr())
                channel_task = asyncio.create_task(self._run_channel())
                assert self._process is not None
                process_task = asyncio.create_task(self._process.wait())

                done, pending = await asyncio.wait(
                    [stderr_task, channel_task, process_task],
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()

            except Exception as e:
                if self._stop_event.is_set():
                    break
                self._logger.warning(f"Service error: {e}, restarting in {backoff}s")
            finally:
                await self._cleanup_channel()

            if not self._auto_restart or self._stop_event.is_set():
                break

            rc = self._process.returncode if self._process else None
            self._logger.warning(
                f"Process exited (code={rc}), restarting in {backoff}s"
            )
            await sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)

    async def _cleanup_channel(self) -> None:
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None

    async def _cleanup_socket(self) -> None:
        try:
            unlink(self._socket_path)
        except FileNotFoundError:
            pass

    async def send(self, data: dict) -> None:
        if self._stub is None:
            raise RuntimeError(f"Service '{self._name}' is not connected")
        envelope = Envelope(**data)
        call = self._stub.Channel(iter([envelope]))  # type: ignore[arg-type]
        async for _ in call:
            pass

    async def stop(self) -> None:
        self._stop_event.set()

        if self._stub is not None:
            try:
                await self._stub.Shutdown(Empty())
            except Exception:
                pass

        if self._process is not None and self._process.returncode is None:
            try:
                await asyncio.wait_for(self._process.wait(), timeout=SHUTDOWN_TIMEOUT)
            except asyncio.TimeoutError:
                self._logger.warning("Process did not exit, killing")
                self._process.kill()
                await self._process.wait()

        await self._cleanup_channel()
        await self._cleanup_socket()
        self._logger.info("Service stopped")
