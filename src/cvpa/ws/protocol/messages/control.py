# -*- coding: utf-8 -*-

from typing import Final, Optional

from pydantic import BaseModel

__all__ = [
    "TYPE_AGENT_SHUTDOWN",
    "TYPE_AGENT_SUSPEND",
    "TYPE_AGENT_ROTATE",
    "AgentShutdown",
    "AgentSuspend",
    "AgentRotate",
]

TYPE_AGENT_SHUTDOWN: Final[str] = "agent.shutdown"
TYPE_AGENT_SUSPEND: Final[str] = "agent.suspend"
TYPE_AGENT_ROTATE: Final[str] = "agent.rotate"


class AgentShutdown(BaseModel):
    deadline_ms: Optional[int] = None


class AgentSuspend(BaseModel):
    pass


class AgentRotate(BaseModel):
    pass
