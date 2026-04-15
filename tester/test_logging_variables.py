# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.logging.variables import (
    DEFAULT_DATEFMT,
    DEFAULT_FORMAT,
    DEFAULT_STYLE,
    default_logging_config,
)


class DefaultLoggingConfigTestCase(TestCase):
    def test_has_version(self):
        config = default_logging_config()
        self.assertEqual(config["version"], 1)

    def test_has_formatters(self):
        config = default_logging_config()
        self.assertIn("default", config["formatters"])
        self.assertIn("colored", config["formatters"])

    def test_has_handlers(self):
        config = default_logging_config()
        self.assertIn("stdout_colored", config["handlers"])
        self.assertIn("root_file", config["handlers"])

    def test_has_loggers(self):
        config = default_logging_config()
        self.assertIn("", config["loggers"])

    def test_custom_logs_dirname(self):
        config = default_logging_config("custom_logs")
        root_file = config["handlers"]["root_file"]
        self.assertIn("custom_logs", root_file["filename"])


class RotatingFileHandlerTestCase(TestCase):
    def test_rotating_file_handler(self):
        from cvpa.logging.variables import _rotating_file_handler

        result = _rotating_file_handler()
        self.assertIn("filename", result)
        self.assertEqual(result["class"], "logging.handlers.RotatingFileHandler")

    def test_timed_rotating_file_handler(self):
        from cvpa.logging.variables import _timed_rotating_file_handler

        result = _timed_rotating_file_handler("test")
        self.assertIn("filename", result)


class ConstantsTestCase(TestCase):
    def test_default_format(self):
        self.assertIsInstance(DEFAULT_FORMAT, str)

    def test_default_datefmt(self):
        self.assertIsInstance(DEFAULT_DATEFMT, str)

    def test_default_style(self):
        self.assertEqual(DEFAULT_STYLE, "%")


if __name__ == "__main__":
    main()
