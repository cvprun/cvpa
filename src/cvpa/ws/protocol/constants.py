# -*- coding: utf-8 -*-

from typing import Final

from cvpa.ws.protocol.messages.control import (
    TYPE_AGENT_ROTATE,
    TYPE_AGENT_SHUTDOWN,
    TYPE_AGENT_SUSPEND,
)
from cvpa.ws.protocol.messages.error import TYPE_SERVER_ERROR
from cvpa.ws.protocol.messages.handshake import (
    TYPE_AGENT_HELLO,
    TYPE_SERVER_HELLO,
)
from cvpa.ws.protocol.messages.heartbeat import (
    TYPE_HEARTBEAT_PING,
    TYPE_HEARTBEAT_PONG,
)

__all__ = [
    "GRACEFUL_SHUTDOWN_MS",
    "HEARTBEAT_INTERVAL_MS",
    "HEARTBEAT_TIMEOUT_MS",
    "HELLO_TIMEOUT_MS",
    "RECONNECT_INITIAL_MS",
    "RECONNECT_JITTER_RATIO",
    "RECONNECT_MAX_MS",
    "TICKET_TTL_MS",
    "TYPE_AGENT_HELLO",
    "TYPE_AGENT_ROTATE",
    "TYPE_AGENT_SHUTDOWN",
    "TYPE_AGENT_STATUS",
    "TYPE_AGENT_SUSPEND",
    "TYPE_HEARTBEAT_PING",
    "TYPE_HEARTBEAT_PONG",
    "TYPE_SERVER_ERROR",
    "TYPE_SERVER_HELLO",
]

HEARTBEAT_INTERVAL_MS: Final[int] = 15_000
HEARTBEAT_TIMEOUT_MS: Final[int] = 45_000
GRACEFUL_SHUTDOWN_MS: Final[int] = 10_000
TICKET_TTL_MS: Final[int] = 30_000
RECONNECT_INITIAL_MS: Final[int] = 1_000
RECONNECT_MAX_MS: Final[int] = 60_000
RECONNECT_JITTER_RATIO: Final[float] = 0.2

HELLO_TIMEOUT_MS: Final[int] = 30_000

TYPE_AGENT_STATUS: Final[str] = "agent.status"
