# -*- coding: utf-8 -*-

from typing import Final, Optional

from pydantic import BaseModel

__all__ = [
    "TYPE_HEARTBEAT_PING",
    "TYPE_HEARTBEAT_PONG",
    "HeartbeatPing",
    "HeartbeatPong",
]

TYPE_HEARTBEAT_PING: Final[str] = "heartbeat.ping"
TYPE_HEARTBEAT_PONG: Final[str] = "heartbeat.pong"


class HeartbeatPing(BaseModel):
    seq: int


class HeartbeatPong(BaseModel):
    seq: Optional[int] = None
