# -*- coding: utf-8 -*-

from typing import Final, List, Optional

from pydantic import BaseModel

__all__ = [
    "TYPE_AGENT_HELLO",
    "TYPE_SERVER_HELLO",
    "AgentHello",
    "ServerHello",
]

TYPE_AGENT_HELLO: Final[str] = "agent.hello"
TYPE_SERVER_HELLO: Final[str] = "server.hello"


class ServerHello(BaseModel):
    session_id: Optional[str] = None
    heartbeat_interval_ms: Optional[int] = None
    heartbeat_timeout_ms: Optional[int] = None


class AgentHello(BaseModel):
    version: str
    capabilities: List[str]
    pid: int
