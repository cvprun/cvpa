# -*- coding: utf-8 -*-

from typing import Final

from pydantic import BaseModel

__all__ = [
    "TYPE_SERVER_ERROR",
    "ServerError",
]

TYPE_SERVER_ERROR: Final[str] = "server.error"


class ServerError(BaseModel):
    code: str
    message: str
