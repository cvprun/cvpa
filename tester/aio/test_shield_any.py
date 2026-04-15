# -*- coding: utf-8 -*-

from logging import Logger
from unittest.mock import MagicMock

from cvpa.aio.shield_any import shield_any


async def test_success():
    async def ok():
        return 42

    logger = MagicMock(spec=Logger)
    result = await shield_any(ok(), logger)
    assert result == 42


async def test_exception():
    async def fail():
        raise ValueError("boom")

    logger = MagicMock(spec=Logger)
    result = await shield_any(fail(), logger)
    assert result is None
    logger.exception.assert_called_once()
