# -*- coding: utf-8 -*-

from unittest.mock import AsyncMock, MagicMock, patch

from cvpa.client.ticket import TicketError
from cvpa.ws.client import AgentConnection
from cvpa.ws.protocol import (
    TYPE_AGENT_ROTATE,
    TYPE_AGENT_SHUTDOWN,
    TYPE_AGENT_SUSPEND,
    TYPE_HEARTBEAT_PONG,
    TYPE_SERVER_HELLO,
    CloseCode,
)
from cvpa.ws.state_machine import AgentEvent, AgentState


def _make_connection(**kwargs) -> AgentConnection:
    logger = kwargs.pop("logger", MagicMock())
    return AgentConnection(
        uri="http://example.com",
        slug="slug",
        token="token",
        logger=logger,
        **kwargs,
    )


async def test_server_hello_transitions_to_active():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    conn._sm.fire(AgentEvent.TICKET_OK)
    assert conn.state is AgentState.HANDSHAKING

    await conn._on_server_hello(
        {
            "type": TYPE_SERVER_HELLO,
            "data": {
                "session_id": "sess-1",
                "heartbeat_interval_ms": 10_000,
                "heartbeat_timeout_ms": 30_000,
            },
        }
    )
    assert conn.state is AgentState.ACTIVE
    assert conn.session_id == "sess-1"
    assert conn._heartbeat_interval_ms == 10_000
    assert conn._heartbeat_timeout_ms == 30_000
    assert conn._hello_event.is_set()


async def test_server_hello_ignored_outside_handshake():
    conn = _make_connection()
    # Still IDLE
    await conn._on_server_hello({"type": TYPE_SERVER_HELLO, "data": {}})
    assert conn.state is AgentState.IDLE


async def test_heartbeat_pong_refreshes():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    conn._sm.fire(AgentEvent.TICKET_OK)
    conn._sm.fire(AgentEvent.SERVER_HELLO)
    assert conn.state is AgentState.ACTIVE

    await conn._on_heartbeat_pong({"type": TYPE_HEARTBEAT_PONG, "data": {"seq": 1}})
    assert conn.state is AgentState.ACTIVE
    assert conn._last_pong_monotonic > 0.0


async def test_agent_shutdown_transitions_to_stopping():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    conn._sm.fire(AgentEvent.TICKET_OK)
    conn._sm.fire(AgentEvent.SERVER_HELLO)

    await conn._on_agent_shutdown(
        {"type": TYPE_AGENT_SHUTDOWN, "data": {"deadline_ms": 2000, "reason": "stop"}}
    )
    assert conn.state is AgentState.STOPPING
    assert conn._graceful_shutdown_ms == 2000
    assert conn._shutdown_close_code == int(CloseCode.SHUTDOWN_REQUESTED)


async def test_agent_suspend_closes_ws_and_stops_loop():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    conn._sm.fire(AgentEvent.TICKET_OK)
    conn._sm.fire(AgentEvent.SERVER_HELLO)
    conn._ws_client = MagicMock()
    conn._ws_client.close = AsyncMock()

    await conn._on_agent_suspend({"type": TYPE_AGENT_SUSPEND, "data": {}})
    assert conn.state is AgentState.SUSPENDED
    assert conn._stop_event.is_set()
    conn._ws_client.close.assert_awaited_once()


async def test_agent_rotate_transitions_to_terminated():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    conn._sm.fire(AgentEvent.TICKET_OK)
    conn._sm.fire(AgentEvent.SERVER_HELLO)
    conn._ws_client = MagicMock()
    conn._ws_client.close = AsyncMock()

    await conn._on_agent_rotate({"type": TYPE_AGENT_ROTATE, "data": {}})
    assert conn.state is AgentState.TERMINATED
    assert conn._stop_event.is_set()


def test_ticket_error_dispatch_auth():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    err = TicketError(401, None, "nope")
    conn._handle_ticket_error(err)
    assert conn.state is AgentState.TERMINATED


def test_ticket_error_dispatch_suspended():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    err = TicketError(403, "agent_suspended", "suspended")
    conn._handle_ticket_error(err)
    assert conn.state is AgentState.SUSPENDED


def test_ticket_error_dispatch_terminating():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    err = TicketError(403, "agent_terminating", "")
    conn._handle_ticket_error(err)
    assert conn.state is AgentState.TERMINATED


def test_ticket_error_dispatch_not_found():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    err = TicketError(404, None, "gone")
    conn._handle_ticket_error(err)
    assert conn.state is AgentState.TERMINATED


def test_ticket_error_dispatch_retryable():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    err = TicketError(503, None, "")
    conn._handle_ticket_error(err)
    assert conn.state is AgentState.BACKOFF


def test_ticket_error_unknown_falls_back_to_retry():
    conn = _make_connection()
    conn._sm.fire(AgentEvent.START)
    err = TicketError(418, None, "teapot")
    conn._handle_ticket_error(err)
    assert conn.state is AgentState.BACKOFF


def test_backoff_delay_bounded_by_max():
    conn = _make_connection(
        reconnect_initial_ms=1000,
        reconnect_max_ms=60_000,
        reconnect_jitter_ratio=0.0,
    )
    assert conn._backoff_delay(0) == 1.0
    assert conn._backoff_delay(5) == 32.0
    assert conn._backoff_delay(100) == 60.0


def test_backoff_delay_nonnegative_with_jitter():
    conn = _make_connection(
        reconnect_initial_ms=1000,
        reconnect_max_ms=60_000,
        reconnect_jitter_ratio=0.5,
    )
    for attempt in range(10):
        for _ in range(20):
            d = conn._backoff_delay(attempt)
            assert d >= 0.0


@patch("cvpa.ws.client.request_ticket")
async def test_request_ticket_offloads_to_executor(mock_request):
    mock_request.return_value = "ws://agent/ws?ticket=X"
    conn = _make_connection()
    url = await conn._request_ticket()
    assert url == "ws://agent/ws?ticket=X"
    mock_request.assert_called_once()
