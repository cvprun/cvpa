# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, Final, Optional

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


class CloseCode(IntEnum):
    NORMAL = 1000
    GOING_AWAY = 1001
    INTERNAL_ERROR = 1011
    HEARTBEAT_TIMEOUT = 4001
    SHUTDOWN_REQUESTED = 4002
    SHUTDOWN_FORCED = 4003
    SUSPENDED = 4010
    TOKEN_ROTATED = 4011
    TOKEN_INVALID = 4012
    TERMINATING = 4020
    DUPLICATE_SESSION = 4030


class ErrorCode:
    MISSING_AUTH: Final[str] = "missing_auth"
    INVALID_TOKEN: Final[str] = "invalid_token"
    TOKEN_VERSION_MISMATCH: Final[str] = "token_version_mismatch"
    AGENT_NOT_FOUND: Final[str] = "agent_not_found"
    AGENT_SUSPENDED: Final[str] = "agent_suspended"
    AGENT_TERMINATING: Final[str] = "agent_terminating"
    AGENT_REMOVED: Final[str] = "agent_removed"
    MISSING_TICKET: Final[str] = "missing_ticket"
    INVALID_TICKET: Final[str] = "invalid_ticket"
    RATE_LIMITED: Final[str] = "rate_limited"
    INTERNAL: Final[str] = "internal"


@dataclass(frozen=True)
class Envelope:
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    id: Optional[str] = None
    ts: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {"type": self.type}
        if self.id is not None:
            out["id"] = self.id
        if self.ts is not None:
            out["ts"] = self.ts
        if self.data:
            out["data"] = self.data
        return out

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Envelope":
        return cls(
            type=raw["type"],
            data=raw.get("data") or {},
            id=raw.get("id"),
            ts=raw.get("ts"),
        )
