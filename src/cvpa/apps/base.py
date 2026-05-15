# -*- coding: utf-8 -*-

import inspect
from abc import ABC, abstractmethod
from asyncio import get_running_loop
from dataclasses import dataclass
from logging import Logger
from typing import (
    Any,
    Awaitable,
    Callable,
    Final,
    List,
    Optional,
    Type,
    TypeVar,
    get_type_hints,
)

from pydantic import BaseModel, ValidationError

from cvpa.ws.handler import MessageDispatcher
from cvpa.ws.protocol.constants import TYPE_SERVER_ERROR
from cvpa.ws.protocol.envelope import Envelope
from cvpa.ws.protocol.error_code import ErrorCode

EnvelopeSender = Callable[[Envelope], Awaitable[None]]

_F = TypeVar("_F", bound=Callable[..., Any])

_ATTR_REQUEST_TYPE: Final[str] = "__cvpa_message_type__"
_ATTR_RESPONSE_TYPE: Final[str] = "__cvpa_response_type__"


def on_message(
    request_type: str,
    response_type: Optional[str] = None,
) -> Callable[[_F], _F]:
    def decorator(func: _F) -> _F:
        setattr(func, _ATTR_REQUEST_TYPE, request_type)
        setattr(func, _ATTR_RESPONSE_TYPE, response_type)
        return func

    return decorator


@dataclass(frozen=True)
class _HandlerSpec:
    method_name: str
    request_type: str
    response_type: Optional[str]
    request_model: Type[BaseModel]
    response_model: Optional[Type[BaseModel]]


class App(ABC):
    def __init__(self) -> None:
        self._sender: Optional[EnvelopeSender] = None
        self._handlers: List[_HandlerSpec] = self._collect_handlers()

    @abstractmethod
    def start(self) -> None: ...

    async def run_async(self, ctx: Any) -> None:
        loop = get_running_loop()
        await loop.run_in_executor(None, self.start)

    def build_dispatcher(self, logger: Optional[Logger] = None) -> MessageDispatcher:
        dispatcher = MessageDispatcher(logger=logger)
        for spec in self._handlers:
            dispatcher.on_text(spec.request_type, self._wrap_handler(spec, logger))
        return dispatcher

    def bind_sender(self, sender: EnvelopeSender) -> None:
        self._sender = sender

    def _collect_handlers(self) -> List[_HandlerSpec]:
        cls = type(self)
        specs: List[_HandlerSpec] = []
        for name, attr in inspect.getmembers(cls, predicate=inspect.isfunction):
            request_type = getattr(attr, _ATTR_REQUEST_TYPE, None)
            if request_type is None:
                continue
            response_type = getattr(attr, _ATTR_RESPONSE_TYPE, None)
            specs.append(
                self._inspect_handler(cls, name, attr, request_type, response_type)
            )
        return specs

    @staticmethod
    def _inspect_handler(
        cls: type,
        name: str,
        func: Callable[..., Any],
        request_type: str,
        response_type: Optional[str],
    ) -> _HandlerSpec:
        qual = f"{cls.__name__}.{name}"

        if not inspect.iscoroutinefunction(func):
            raise TypeError(f"{qual}: @on_message handler must be async")

        sig = inspect.signature(func)
        params = [p for p in sig.parameters.values() if p.name != "self"]
        if len(params) != 1:
            raise TypeError(
                f"{qual}: @on_message handler must take exactly one "
                f"request parameter besides self"
            )

        try:
            hints = get_type_hints(func)
        except Exception as e:
            raise TypeError(f"{qual}: failed to resolve type hints: {e}") from e

        req_param = params[0]
        req_model = hints.get(req_param.name)
        if not (isinstance(req_model, type) and issubclass(req_model, BaseModel)):
            raise TypeError(
                f"{qual}: parameter '{req_param.name}' must be annotated "
                f"with a pydantic.BaseModel subclass"
            )

        ret_anno = hints.get("return", type(None))
        if ret_anno is type(None):
            resp_model: Optional[Type[BaseModel]] = None
        elif isinstance(ret_anno, type) and issubclass(ret_anno, BaseModel):
            resp_model = ret_anno
        else:
            raise TypeError(
                f"{qual}: return annotation must be a pydantic.BaseModel "
                f"subclass or None"
            )

        if resp_model is not None and response_type is None:
            raise TypeError(
                f"{qual}: response model declared but response_type "
                f"missing in @on_message"
            )
        if resp_model is None and response_type is not None:
            raise TypeError(
                f"{qual}: response_type declared but return annotation is None"
            )

        return _HandlerSpec(
            method_name=name,
            request_type=request_type,
            response_type=response_type,
            request_model=req_model,
            response_model=resp_model,
        )

    def _wrap_handler(
        self,
        spec: _HandlerSpec,
        logger: Optional[Logger] = None,
    ) -> Callable[[Any], Awaitable[None]]:
        bound = getattr(self, spec.method_name)

        async def handle(data: Any) -> None:
            envelope = Envelope.from_dict(data)
            try:
                request = spec.request_model.model_validate(envelope.data)
            except ValidationError as e:
                await self._send_error(envelope, ErrorCode.VALIDATION_ERROR, str(e))
                return

            try:
                response = await bound(request)
            except Exception as e:
                if logger is not None:
                    logger.exception(
                        f"@on_message handler {spec.request_type} failed: {e}"
                    )
                await self._send_error(envelope, ErrorCode.HANDLER_ERROR, str(e))
                return

            if response is None or spec.response_type is None:
                return
            if self._sender is None:
                return
            reply = Envelope(
                type=spec.response_type,
                data=response.model_dump(),
                id=envelope.id,
            )
            await self._sender(reply)

        return handle

    async def _send_error(
        self, request_envelope: Envelope, code: str, message: str
    ) -> None:
        if self._sender is None:
            return
        await self._sender(
            Envelope(
                type=TYPE_SERVER_ERROR,
                data={"code": code, "message": message},
                id=request_envelope.id,
            )
        )
