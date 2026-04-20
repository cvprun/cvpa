# -*- coding: utf-8 -*-

from enum import Enum
from logging import Logger
from typing import Final, Optional, Tuple


class AgentState(str, Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    HANDSHAKING = "handshaking"
    ACTIVE = "active"
    STOPPING = "stopping"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    BACKOFF = "backoff"


class AgentEvent(str, Enum):
    START = "start"
    TICKET_OK = "ticket_ok"
    TICKET_AUTH_FAIL = "ticket_auth_fail"
    TICKET_SUSPENDED = "ticket_suspended"
    TICKET_TERMINATING = "ticket_terminating"
    TICKET_NOT_FOUND = "ticket_not_found"
    TICKET_RETRYABLE = "ticket_retryable"
    SERVER_HELLO = "server_hello"
    HANDSHAKE_TIMEOUT = "handshake_timeout"
    HEARTBEAT_PONG = "heartbeat_pong"
    HEARTBEAT_TIMEOUT = "heartbeat_timeout"
    AGENT_SHUTDOWN = "agent_shutdown"
    AGENT_SUSPEND = "agent_suspend"
    AGENT_ROTATE = "agent_rotate"
    WS_CLOSED = "ws_closed"
    CLEANUP_DONE = "cleanup_done"
    CLEANUP_DEADLINE = "cleanup_deadline"
    BACKOFF_EXPIRED = "backoff_expired"


_TRANSITIONS: Final[dict[Tuple[AgentState, AgentEvent], AgentState]] = {
    (AgentState.IDLE, AgentEvent.START): AgentState.CONNECTING,
    (AgentState.CONNECTING, AgentEvent.TICKET_OK): AgentState.HANDSHAKING,
    (AgentState.CONNECTING, AgentEvent.TICKET_AUTH_FAIL): AgentState.TERMINATED,
    (AgentState.CONNECTING, AgentEvent.TICKET_SUSPENDED): AgentState.SUSPENDED,
    (AgentState.CONNECTING, AgentEvent.TICKET_TERMINATING): AgentState.TERMINATED,
    (AgentState.CONNECTING, AgentEvent.TICKET_NOT_FOUND): AgentState.TERMINATED,
    (AgentState.CONNECTING, AgentEvent.TICKET_RETRYABLE): AgentState.BACKOFF,
    (AgentState.CONNECTING, AgentEvent.WS_CLOSED): AgentState.BACKOFF,
    (AgentState.HANDSHAKING, AgentEvent.SERVER_HELLO): AgentState.ACTIVE,
    (AgentState.HANDSHAKING, AgentEvent.HANDSHAKE_TIMEOUT): AgentState.BACKOFF,
    (AgentState.HANDSHAKING, AgentEvent.WS_CLOSED): AgentState.BACKOFF,
    (AgentState.ACTIVE, AgentEvent.HEARTBEAT_PONG): AgentState.ACTIVE,
    (AgentState.ACTIVE, AgentEvent.HEARTBEAT_TIMEOUT): AgentState.BACKOFF,
    (AgentState.ACTIVE, AgentEvent.AGENT_SHUTDOWN): AgentState.STOPPING,
    (AgentState.ACTIVE, AgentEvent.AGENT_SUSPEND): AgentState.SUSPENDED,
    (AgentState.ACTIVE, AgentEvent.AGENT_ROTATE): AgentState.TERMINATED,
    (AgentState.ACTIVE, AgentEvent.WS_CLOSED): AgentState.BACKOFF,
    (AgentState.STOPPING, AgentEvent.CLEANUP_DONE): AgentState.STOPPED,
    (AgentState.STOPPING, AgentEvent.CLEANUP_DEADLINE): AgentState.STOPPED,
    (AgentState.BACKOFF, AgentEvent.BACKOFF_EXPIRED): AgentState.CONNECTING,
}


class InvalidTransitionError(Exception):
    def __init__(self, state: AgentState, event: AgentEvent) -> None:
        super().__init__(f"Invalid transition: {state.value} -{event.value}->")
        self.state = state
        self.event = event


class ConnectionStateMachine:
    def __init__(
        self,
        *,
        initial: AgentState = AgentState.IDLE,
        logger: Optional[Logger] = None,
    ) -> None:
        self._state = initial
        self._logger = logger

    @property
    def state(self) -> AgentState:
        return self._state

    @staticmethod
    def peek(state: AgentState, event: AgentEvent) -> Optional[AgentState]:
        return _TRANSITIONS.get((state, event))

    def can(self, event: AgentEvent) -> bool:
        return (self._state, event) in _TRANSITIONS

    def fire(self, event: AgentEvent) -> AgentState:
        nxt = _TRANSITIONS.get((self._state, event))
        if nxt is None:
            raise InvalidTransitionError(self._state, event)
        prev = self._state
        self._state = nxt
        if self._logger is not None:
            self._logger.info(
                "agent.transition",
                extra={
                    "from": prev.value,
                    "to": nxt.value,
                    "event": event.value,
                },
            )
        return nxt

    def is_terminal(self) -> bool:
        return self._state is AgentState.TERMINATED

    def reset(self, state: AgentState = AgentState.IDLE) -> None:
        self._state = state
