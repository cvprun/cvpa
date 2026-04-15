# -*- coding: utf-8 -*-

import json
from unittest.mock import AsyncMock, MagicMock

from cvpa.ws.handler import MessageDispatcher


async def test_binary_with_handler():
    handler = AsyncMock()
    d = MessageDispatcher()
    d.on_binary(handler)
    await d.dispatch(b"data")
    handler.assert_awaited_once_with(b"data")


async def test_binary_no_handler_with_logger():
    logger = MagicMock()
    d = MessageDispatcher(logger=logger)
    await d.dispatch(b"data")
    logger.debug.assert_called_once()


async def test_binary_no_handler_no_logger():
    d = MessageDispatcher()
    await d.dispatch(b"data")


async def test_text_with_registered_handler():
    handler = AsyncMock()
    d = MessageDispatcher()
    d.on_text("greeting", handler)
    await d.dispatch(json.dumps({"type": "greeting", "msg": "hi"}))
    handler.assert_awaited_once()


async def test_text_missing_type_with_on_unknown():
    on_unknown = AsyncMock()
    d = MessageDispatcher(on_unknown=on_unknown)
    await d.dispatch(json.dumps({"msg": "hi"}))
    on_unknown.assert_awaited_once()


async def test_text_missing_type_no_unknown_with_logger():
    logger = MagicMock()
    d = MessageDispatcher(logger=logger)
    await d.dispatch(json.dumps({"msg": "hi"}))
    logger.warning.assert_called_once()


async def test_text_missing_type_no_unknown_no_logger():
    d = MessageDispatcher()
    await d.dispatch(json.dumps({"msg": "hi"}))


async def test_text_unregistered_type_with_on_unknown():
    on_unknown = AsyncMock()
    d = MessageDispatcher(on_unknown=on_unknown)
    await d.dispatch(json.dumps({"type": "unknown_type"}))
    on_unknown.assert_awaited_once()


async def test_text_unregistered_type_no_unknown_with_logger():
    logger = MagicMock()
    d = MessageDispatcher(logger=logger)
    await d.dispatch(json.dumps({"type": "unknown_type"}))
    logger.debug.assert_called_once()


async def test_text_unregistered_type_no_unknown_no_logger():
    d = MessageDispatcher()
    await d.dispatch(json.dumps({"type": "unknown_type"}))


async def test_call():
    handler = AsyncMock()
    d = MessageDispatcher()
    d.on_text("test", handler)
    await d(json.dumps({"type": "test"}))
    handler.assert_awaited_once()


async def test_custom_type_field():
    handler = AsyncMock()
    d = MessageDispatcher(type_field="action")
    d.on_text("do_it", handler)
    await d.dispatch(json.dumps({"action": "do_it"}))
    handler.assert_awaited_once()
