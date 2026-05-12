# -*- coding: utf-8 -*-

from typing import Final

HEARTBEAT_INTERVAL_MS: Final[int] = 15_000
HEARTBEAT_TIMEOUT_MS: Final[int] = 45_000
GRACEFUL_SHUTDOWN_MS: Final[int] = 10_000
TICKET_TTL_MS: Final[int] = 30_000
RECONNECT_INITIAL_MS: Final[int] = 1_000
RECONNECT_MAX_MS: Final[int] = 60_000
RECONNECT_JITTER_RATIO: Final[float] = 0.2

HELLO_TIMEOUT_MS: Final[int] = 30_000

TYPE_AGENT_HELLO: Final[str] = "agent.hello"
TYPE_SERVER_HELLO: Final[str] = "server.hello"
TYPE_HEARTBEAT_PING: Final[str] = "heartbeat.ping"
TYPE_HEARTBEAT_PONG: Final[str] = "heartbeat.pong"
TYPE_AGENT_STATUS: Final[str] = "agent.status"
TYPE_AGENT_SHUTDOWN: Final[str] = "agent.shutdown"
TYPE_AGENT_SUSPEND: Final[str] = "agent.suspend"
TYPE_AGENT_ROTATE: Final[str] = "agent.rotate"
TYPE_SERVER_ERROR: Final[str] = "server.error"
