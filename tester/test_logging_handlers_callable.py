# -*- coding: utf-8 -*-

import logging
from unittest import TestCase, main
from unittest.mock import MagicMock

from cvpa.logging.handlers.callable import CallableHandler


class CallableHandlerTestCase(TestCase):
    def test_emit_calls_callback(self):
        callback = MagicMock()
        handler = CallableHandler(callback)
        handler.setFormatter(logging.Formatter("%(message)s"))

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello",
            args=None,
            exc_info=None,
        )
        handler.emit(record)
        callback.assert_called_once()
        args = callback.call_args[0]
        self.assertIs(args[0], record)
        self.assertIn("hello", args[1])


if __name__ == "__main__":
    main()
