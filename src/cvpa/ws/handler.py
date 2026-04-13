# -*- coding: utf-8 -*-

import json
from logging import Logger
from typing import Any, Awaitable, Callable, Dict, Optional, Union

MessageHandlerCallable = Callable[[Any], Awaitable[None]]


class MessageDispatcher:
    def __init__(
        self,
        *,
        type_field: str = "type",
        on_unknown: Optional[MessageHandlerCallable] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        self._type_field = type_field
        self._text_handlers: Dict[str, MessageHandlerCallable] = {}
        self._binary_handler: Optional[MessageHandlerCallable] = None
        self._on_unknown = on_unknown
        self._logger = logger

    def on_text(self, type_key: str, handler: MessageHandlerCallable) -> None:
        self._text_handlers[type_key] = handler

    def on_binary(self, handler: MessageHandlerCallable) -> None:
        self._binary_handler = handler

    async def dispatch(self, raw: Union[str, bytes]) -> None:
        if isinstance(raw, bytes):
            if self._binary_handler:
                await self._binary_handler(raw)
            elif self._logger:
                self._logger.debug(f"No binary handler, ignoring: {raw!r}")
            return

        data: Any = json.loads(raw)
        type_key = data.get(self._type_field)

        if type_key is None:
            if self._on_unknown:
                await self._on_unknown(data)
            elif self._logger:
                self._logger.warning(
                    f"Message missing '{self._type_field}' field: {raw}"
                )
            return

        handler = self._text_handlers.get(type_key)
        if handler:
            await handler(data)
        elif self._on_unknown:
            await self._on_unknown(data)
        elif self._logger:
            self._logger.debug(f"No handler for message type: {type_key}")

    async def __call__(self, raw: Union[str, bytes]) -> None:
        await self.dispatch(raw)
