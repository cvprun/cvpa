# -*- coding: utf-8 -*-

import tempfile
from unittest import TestCase, main

from cvpa.logging.handlers.file import TimedRotatingFileHandler


class TimedRotatingFileHandlerTestCase(TestCase):
    def test_without_suffix(self):
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            handler = TimedRotatingFileHandler(f.name)
            self.assertIsNotNone(handler)
            handler.close()

    def test_with_suffix(self):
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            handler = TimedRotatingFileHandler(f.name, suffix="%Y%m%d.log")
            self.assertEqual(handler.suffix, "%Y%m%d.log")
            handler.close()


if __name__ == "__main__":
    main()
