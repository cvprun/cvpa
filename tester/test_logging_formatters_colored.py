# -*- coding: utf-8 -*-

import logging
from unittest import TestCase, main

from cvpa.logging.formatters.colored import ColoredFormatter


class ColoredFormatterTestCase(TestCase):
    def test_default_init(self):
        f = ColoredFormatter()
        self.assertIsNotNone(f)

    def test_custom_args(self):
        f = ColoredFormatter(
            fmt="%(message)s",
            datefmt="%Y-%m-%d",
            style="%",
        )
        self.assertIsNotNone(f)

    def test_format_record(self):
        f = ColoredFormatter(fmt="%(message)s")
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="hello",
            args=None,
            exc_info=None,
        )
        result = f.format(record)
        self.assertIn("hello", result)


if __name__ == "__main__":
    main()
