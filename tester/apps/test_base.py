# -*- coding: utf-8 -*-

import json
from typing import Any, List
from unittest import main
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from cvpa.apps.base import App, on_message
from cvpa.ws.protocol.constants import TYPE_SERVER_ERROR
from cvpa.ws.protocol.envelope import Envelope
from cvpa.ws.protocol.error_code import ErrorCode

_REQ_TYPE = "test.req"
_RESP_TYPE = "test.resp"


class _Req(BaseModel):
    x: int


class _Resp(BaseModel):
    y: int


class _DummyApp(App):
    def __init__(self) -> None:
        super().__init__()
        self.calls: List[_Req] = []

    def start(self) -> None:
        return None

    async def run_async(self, ctx: Any) -> None:
        return None

    @on_message(_REQ_TYPE, response_type=_RESP_TYPE)
    async def on_req(self, request: _Req) -> _Resp:
        self.calls.append(request)
        return _Resp(y=request.x + 1)


async def test_roundtrip_envelope() -> None:
    app = _DummyApp()
    sender = AsyncMock()
    app.bind_sender(sender)
    dispatcher = app.build_dispatcher()

    raw = json.dumps({"type": _REQ_TYPE, "data": {"x": 41}, "id": "abc"})
    await dispatcher.dispatch(raw)

    assert len(app.calls) == 1
    assert app.calls[0].x == 41
    sender.assert_awaited_once()
    assert sender.await_args is not None
    reply: Envelope = sender.await_args.args[0]
    assert reply.type == _RESP_TYPE
    assert reply.data == {"y": 42}
    assert reply.id == "abc"


def test_non_basemodel_param_raises_typeerror() -> None:
    class _Bad(App):
        def start(self) -> None:
            return None

        async def run_async(self, ctx: Any) -> None:
            return None

        @on_message(_REQ_TYPE)
        async def handle(self, request: int) -> None:
            return None

    with pytest.raises(TypeError):
        _Bad()


async def test_validation_error_emits_server_error() -> None:
    app = _DummyApp()
    sender = AsyncMock()
    app.bind_sender(sender)
    dispatcher = app.build_dispatcher()

    raw = json.dumps({"type": _REQ_TYPE, "data": {}, "id": "xyz"})
    await dispatcher.dispatch(raw)

    sender.assert_awaited_once()
    assert sender.await_args is not None
    err: Envelope = sender.await_args.args[0]
    assert err.type == TYPE_SERVER_ERROR
    assert err.data["code"] == ErrorCode.VALIDATION_ERROR
    assert err.id == "xyz"


if __name__ == "__main__":
    main()
