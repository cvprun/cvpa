# -*- coding: utf-8 -*-

from enum import Enum


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
