# -*- coding: utf-8 -*-

from enum import Enum


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
