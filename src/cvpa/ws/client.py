# -*- coding: utf-8 -*-

import asyncio
import json
import os
import random
from asyncio import Event, Task, get_running_loop, sleep, wait_for
from datetime import datetime, timezone
from logging import Logger
from typing import Any, Awaitable, Callable, Dict, Final, Optional, Union

from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed

from cvpa.client.ticket import TicketError, request_ticket
from cvpa.ws.handler import MessageDispatcher
from cvpa.ws.protocol import (
    GRACEFUL_SHUTDOWN_MS,
    HEARTBEAT_INTERVAL_MS,
    HEARTBEAT_TIMEOUT_MS,
    HELLO_TIMEOUT_MS,
    RECONNECT_INITIAL_MS,
    RECONNECT_JITTER_RATIO,
    RECONNECT_MAX_MS,
    TYPE_AGENT_HELLO,
    TYPE_AGENT_ROTATE,
    TYPE_AGENT_SHUTDOWN,
    TYPE_AGENT_SUSPEND,
    TYPE_HEARTBEAT_PING,
    TYPE_HEARTBEAT_PONG,
    TYPE_SERVER_ERROR,
    TYPE_SERVER_HELLO,
    CloseCode,
    Envelope,
)
from cvpa.ws.state_machine import AgentEvent, AgentState, ConnectionStateMachine

INITIAL_BACKOFF: Final[float] = 1.0
MAX_BACKOFF: Final[float] = 60.0

OnMessageCallback = Callable[[Union[str, bytes]], Awaitable[None]]
GetUrlCallback = Callable[[], Awaitable[str]]
AsyncNoArg = Callable[[], Awaitable[None]]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


class AgentConnection:
    """상태 머신이 주도하는 재연결/heartbeat/shutdown 관리자."""

    def __init__(
        self,
        uri: str,
        slug: str,
        token: str,
        *,
        dispatcher: Optional[MessageDispatcher] = None,
        on_active: Optional[AsyncNoArg] = None,
        on_deactive: Optional[AsyncNoArg] = None,
        logger: Optional[Logger] = None,
        legacy_protocol: bool = False,
        heartbeat_interval_ms: int = HEARTBEAT_INTERVAL_MS,
        heartbeat_timeout_ms: int = HEARTBEAT_TIMEOUT_MS,
        hello_timeout_ms: int = HELLO_TIMEOUT_MS,
        graceful_shutdown_ms: int = GRACEFUL_SHUTDOWN_MS,
        reconnect_initial_ms: int = RECONNECT_INITIAL_MS,
        reconnect_max_ms: int = RECONNECT_MAX_MS,
        reconnect_jitter_ratio: float = RECONNECT_JITTER_RATIO,
        agent_version: str = "",
        capabilities: Optional[list[str]] = None,
    ) -> None:
        self._uri = uri
        self._slug = slug
        self._token = token
        self._logger = logger
        self._legacy = legacy_protocol

        self._heartbeat_interval_ms = heartbeat_interval_ms
        self._heartbeat_timeout_ms = heartbeat_timeout_ms
        self._hello_timeout_ms = hello_timeout_ms
        self._graceful_shutdown_ms = graceful_shutdown_ms
        self._reconnect_initial_ms = reconnect_initial_ms
        self._reconnect_max_ms = reconnect_max_ms
        self._reconnect_jitter_ratio = reconnect_jitter_ratio
        self._agent_version = agent_version
        self._capabilities = list(capabilities or [])

        self._sm = ConnectionStateMachine(logger=logger)
        self._stop_event = Event()
        self._ws_client: Optional[WebSocketClient] = None
        self._session_id: Optional[str] = None
        self._heartbeat_seq = 0
        self._heartbeat_task: Optional[Task[None]] = None
        self._last_pong_monotonic: float = 0.0
        self._hello_event = Event()
        self._shutdown_close_code = int(CloseCode.NORMAL)

        self._dispatcher = dispatcher or MessageDispatcher(logger=logger)
        self._register_handlers(self._dispatcher)

        self._on_active = on_active
        self._on_deactive = on_deactive

    @property
    def state(self) -> AgentState:
        return self._sm.state

    @property
    def session_id(self) -> Optional[str]:
        return self._session_id

    @property
    def dispatcher(self) -> MessageDispatcher:
        return self._dispatcher

    def _register_handlers(self, dispatcher: MessageDispatcher) -> None:
        dispatcher.on_text(TYPE_SERVER_HELLO, self._on_server_hello)
        dispatcher.on_text(TYPE_HEARTBEAT_PONG, self._on_heartbeat_pong)
        dispatcher.on_text(TYPE_AGENT_SHUTDOWN, self._on_agent_shutdown)
        dispatcher.on_text(TYPE_AGENT_SUSPEND, self._on_agent_suspend)
        dispatcher.on_text(TYPE_AGENT_ROTATE, self._on_agent_rotate)
        dispatcher.on_text(TYPE_SERVER_ERROR, self._on_server_error)

    # ------------------------------------------------------------------
    # Ticket request
    # ------------------------------------------------------------------

    async def _request_ticket(self) -> str:
        loop = get_running_loop()
        return await loop.run_in_executor(
            None, request_ticket, self._uri, self._slug, self._token, self._logger
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------

    async def _on_server_hello(self, data: Dict[str, Any]) -> None:
        payload = data.get("data") or {}
        session_id = payload.get("session_id")
        interval = payload.get("heartbeat_interval_ms")
        timeout = payload.get("heartbeat_timeout_ms")
        if isinstance(session_id, str):
            self._session_id = session_id
        if isinstance(interval, int) and interval > 0:
            self._heartbeat_interval_ms = interval
        if isinstance(timeout, int) and timeout > 0:
            self._heartbeat_timeout_ms = timeout

        if self._sm.state is AgentState.HANDSHAKING:
            self._sm.fire(AgentEvent.SERVER_HELLO)
            self._hello_event.set()

    async def _on_heartbeat_pong(self, data: Dict[str, Any]) -> None:
        if self._sm.state is AgentState.ACTIVE:
            loop = get_running_loop()
            self._last_pong_monotonic = loop.time()
            self._sm.fire(AgentEvent.HEARTBEAT_PONG)

    async def _on_agent_shutdown(self, data: Dict[str, Any]) -> None:
        payload = data.get("data") or {}
        deadline = payload.get("deadline_ms", self._graceful_shutdown_ms)
        if not isinstance(deadline, int) or deadline <= 0:
            deadline = self._graceful_shutdown_ms
        self._graceful_shutdown_ms = deadline
        if self._sm.can(AgentEvent.AGENT_SHUTDOWN):
            self._sm.fire(AgentEvent.AGENT_SHUTDOWN)
            self._shutdown_close_code = int(CloseCode.SHUTDOWN_REQUESTED)

    async def _on_agent_suspend(self, data: Dict[str, Any]) -> None:
        if self._sm.can(AgentEvent.AGENT_SUSPEND):
            self._sm.fire(AgentEvent.AGENT_SUSPEND)
            self._shutdown_close_code = int(CloseCode.SUSPENDED)
            await self._close_ws(int(CloseCode.SUSPENDED), "suspended")
            self._stop_event.set()

    async def _on_agent_rotate(self, data: Dict[str, Any]) -> None:
        if self._sm.can(AgentEvent.AGENT_ROTATE):
            self._sm.fire(AgentEvent.AGENT_ROTATE)
            self._shutdown_close_code = int(CloseCode.TOKEN_ROTATED)
            await self._close_ws(int(CloseCode.TOKEN_ROTATED), "token_rotated")
            self._stop_event.set()

    async def _on_server_error(self, data: Dict[str, Any]) -> None:
        if self._logger:
            self._logger.warning(f"server.error: {data.get('data')}")

    # ------------------------------------------------------------------
    # Sending
    # ------------------------------------------------------------------

    async def _send_envelope(self, env: Envelope) -> None:
        if self._ws_client is None:
            return
        obj = env.to_dict()
        obj.setdefault("ts", _now_iso())
        await self._ws_client.send_json(obj)

    async def _send_hello(self) -> None:
        await self._send_envelope(
            Envelope(
                type=TYPE_AGENT_HELLO,
                data={
                    "version": self._agent_version,
                    "capabilities": self._capabilities,
                    "pid": os.getpid(),
                    "legacy": self._legacy,
                },
            )
        )

    async def _send_ping(self) -> None:
        self._heartbeat_seq += 1
        await self._send_envelope(
            Envelope(
                type=TYPE_HEARTBEAT_PING,
                data={"seq": self._heartbeat_seq},
            )
        )

    # ------------------------------------------------------------------
    # Heartbeat
    # ------------------------------------------------------------------

    async def _heartbeat_loop(self) -> None:
        loop = get_running_loop()
        interval = self._heartbeat_interval_ms / 1000.0
        timeout = self._heartbeat_timeout_ms / 1000.0
        self._last_pong_monotonic = loop.time()
        try:
            while self._sm.state is AgentState.ACTIVE:
                await sleep(interval)
                if self._sm.state is not AgentState.ACTIVE:
                    return
                if loop.time() - self._last_pong_monotonic > timeout:
                    if self._logger:
                        self._logger.warning("Heartbeat timeout")
                    if self._sm.can(AgentEvent.HEARTBEAT_TIMEOUT):
                        self._sm.fire(AgentEvent.HEARTBEAT_TIMEOUT)
                    await self._close_ws(
                        int(CloseCode.INTERNAL_ERROR), "heartbeat_timeout"
                    )
                    return
                try:
                    await self._send_ping()
                except Exception as exc:  # noqa: BLE001
                    if self._logger:
                        self._logger.debug(f"Ping send failed: {exc}")
                    return
        except asyncio.CancelledError:
            raise

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def _close_ws(self, code: int, reason: str) -> None:
        if self._ws_client is not None:
            await self._ws_client.close(code=code, reason=reason)

    async def _await_hello(self) -> bool:
        try:
            await wait_for(
                self._hello_event.wait(), timeout=self._hello_timeout_ms / 1000.0
            )
            return True
        except asyncio.TimeoutError:
            return False

    async def _run_session(self) -> None:
        assert self._sm.state is AgentState.CONNECTING

        try:
            ws_url = await self._request_ticket()
        except TicketError as exc:
            self._handle_ticket_error(exc)
            return
        except Exception as exc:  # noqa: BLE001
            if self._logger:
                self._logger.warning(f"Ticket request failed: {exc}")
            if self._sm.can(AgentEvent.TICKET_RETRYABLE):
                self._sm.fire(AgentEvent.TICKET_RETRYABLE)
            return

        if self._sm.can(AgentEvent.TICKET_OK):
            self._sm.fire(AgentEvent.TICKET_OK)
        else:
            return

        self._hello_event.clear()
        self._ws_client = WebSocketClient(
            get_url=self._only_url(ws_url),
            on_message=self._dispatcher,
            logger=self._logger,
        )

        try:
            await self._ws_client._connect()
        except Exception as exc:  # noqa: BLE001
            if self._logger:
                self._logger.warning(f"WebSocket connect failed: {exc}")
            if self._sm.can(AgentEvent.WS_CLOSED):
                self._sm.fire(AgentEvent.WS_CLOSED)
            return

        try:
            await self._send_hello()
        except Exception as exc:  # noqa: BLE001
            if self._logger:
                self._logger.warning(f"Hello send failed: {exc}")
            await self._close_ws(int(CloseCode.INTERNAL_ERROR), "hello_failed")
            if self._sm.can(AgentEvent.WS_CLOSED):
                self._sm.fire(AgentEvent.WS_CLOSED)
            return

        listen_task = asyncio.create_task(self._ws_client._listen())

        hello_ok = await self._await_hello()
        if not hello_ok:
            if self._logger:
                self._logger.warning("server.hello timeout")
            if self._sm.can(AgentEvent.HANDSHAKE_TIMEOUT):
                self._sm.fire(AgentEvent.HANDSHAKE_TIMEOUT)
            await self._close_ws(int(CloseCode.INTERNAL_ERROR), "hello_timeout")
            await self._finalize_listen(listen_task)
            return

        if self._on_active is not None:
            try:
                await self._on_active()
            except Exception as exc:  # noqa: BLE001
                if self._logger:
                    self._logger.exception(f"on_active hook failed: {exc}")

        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        try:
            await listen_task
        except Exception as exc:  # noqa: BLE001
            if self._logger:
                self._logger.debug(f"Listen loop exited: {exc}")
        finally:
            await self._end_session()

    async def _end_session(self) -> None:
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001
                pass
            self._heartbeat_task = None

        if self._sm.state is AgentState.STOPPING:
            if self._on_deactive is not None:
                try:
                    await wait_for(
                        self._on_deactive(),
                        timeout=self._graceful_shutdown_ms / 1000.0,
                    )
                    self._sm.fire(AgentEvent.CLEANUP_DONE)
                except asyncio.TimeoutError:
                    if self._logger:
                        self._logger.warning("Graceful shutdown deadline exceeded")
                    self._sm.fire(AgentEvent.CLEANUP_DEADLINE)
            else:
                self._sm.fire(AgentEvent.CLEANUP_DONE)
            await self._close_ws(
                self._shutdown_close_code or int(CloseCode.SHUTDOWN_REQUESTED),
                "shutdown",
            )
            self._stop_event.set()
            return

        if self._sm.state is AgentState.ACTIVE:
            if self._on_deactive is not None:
                try:
                    await self._on_deactive()
                except Exception as exc:  # noqa: BLE001
                    if self._logger:
                        self._logger.debug(f"on_deactive failed: {exc}")
            if self._sm.can(AgentEvent.WS_CLOSED):
                self._sm.fire(AgentEvent.WS_CLOSED)

    async def _finalize_listen(self, task: Task[None]) -> None:
        task.cancel()
        try:
            await task
        except (asyncio.CancelledError, Exception):  # noqa: BLE001
            pass

    def _only_url(self, url: str) -> GetUrlCallback:
        async def _get() -> str:
            return url

        return _get

    def _handle_ticket_error(self, exc: TicketError) -> None:
        if self._logger:
            self._logger.warning(str(exc))
        if exc.is_auth_failure:
            self._sm.fire(AgentEvent.TICKET_AUTH_FAIL)
        elif exc.is_suspended:
            self._sm.fire(AgentEvent.TICKET_SUSPENDED)
        elif exc.is_terminating:
            self._sm.fire(AgentEvent.TICKET_TERMINATING)
        elif exc.is_not_found:
            self._sm.fire(AgentEvent.TICKET_NOT_FOUND)
        elif exc.is_retryable:
            self._sm.fire(AgentEvent.TICKET_RETRYABLE)
        else:
            self._sm.fire(AgentEvent.TICKET_RETRYABLE)

    def _backoff_delay(self, attempt: int) -> float:
        delay_ms = min(
            self._reconnect_initial_ms * (2**attempt),
            self._reconnect_max_ms,
        )
        jitter = delay_ms * random.uniform(
            -self._reconnect_jitter_ratio, self._reconnect_jitter_ratio
        )
        return max(0.0, (delay_ms + jitter) / 1000.0)

    # ------------------------------------------------------------------
    # Public loop
    # ------------------------------------------------------------------

    async def start(self) -> None:
        if self._sm.state is AgentState.IDLE:
            self._sm.fire(AgentEvent.START)

        attempt = 0
        while not self._stop_event.is_set():
            state = self._sm.state
            if state is AgentState.CONNECTING:
                await self._run_session()
                if self._sm.state is AgentState.ACTIVE:
                    attempt = 0
                continue
            if state is AgentState.BACKOFF:
                delay = self._backoff_delay(attempt)
                if self._logger:
                    self._logger.info(f"Reconnecting in {delay:.1f}s")
                try:
                    await wait_for(self._stop_event.wait(), timeout=delay)
                    break
                except asyncio.TimeoutError:
                    pass
                if self._sm.can(AgentEvent.BACKOFF_EXPIRED):
                    self._sm.fire(AgentEvent.BACKOFF_EXPIRED)
                attempt = min(attempt + 1, 30)
                continue
            if state is AgentState.STOPPED:
                if self._logger:
                    self._logger.info("Agent stopped; waiting for external restart")
                await self._stop_event.wait()
                break
            if state is AgentState.SUSPENDED:
                if self._logger:
                    self._logger.info("Agent suspended; exiting reconnect loop")
                break
            if state is AgentState.TERMINATED:
                if self._logger:
                    self._logger.info("Agent terminated; exiting")
                break
            # IDLE/HANDSHAKING/ACTIVE/STOPPING 은 내부 전이 중이므로 짧게 양보.
            await sleep(0.01)

    async def stop(self) -> None:
        self._stop_event.set()
        await self._close_ws(int(CloseCode.GOING_AWAY), "going_away")
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
