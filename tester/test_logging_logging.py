# -*- coding: utf-8 -*-

import logging
import tempfile
from unittest import TestCase, main
from unittest.mock import patch

from cvpa.logging.logging import (
    OFF,
    add_default_colored_logging,
    add_default_logging,
    add_default_rotate_file_logging,
    add_simple_logging,
    convert_level_number,
    convert_printable_level,
    dumps_default_logging_config,
    loads_logging_config,
    set_asyncio_level,
    set_default_logging_config,
    set_root_level,
)


class ConvertLevelNumberTestCase(TestCase):
    def test_none(self):
        self.assertEqual(convert_level_number(None), logging.DEBUG)

    def test_critical(self):
        self.assertEqual(convert_level_number("critical"), logging.CRITICAL)

    def test_fatal(self):
        self.assertEqual(convert_level_number("fatal"), logging.FATAL)

    def test_error(self):
        self.assertEqual(convert_level_number("error"), logging.ERROR)

    def test_warning(self):
        self.assertEqual(convert_level_number("warning"), logging.WARNING)

    def test_warn(self):
        self.assertEqual(convert_level_number("warn"), logging.WARN)

    def test_info(self):
        self.assertEqual(convert_level_number("info"), logging.INFO)

    def test_debug(self):
        self.assertEqual(convert_level_number("debug"), logging.DEBUG)

    def test_notset(self):
        self.assertEqual(convert_level_number("notset"), logging.NOTSET)

    def test_off(self):
        self.assertEqual(convert_level_number("off"), OFF)

    def test_numeric_string(self):
        self.assertEqual(convert_level_number("10"), 10)

    def test_invalid_string(self):
        with self.assertRaises(ValueError):
            convert_level_number("invalid")

    def test_int_passthrough(self):
        self.assertEqual(convert_level_number(42), 42)

    def test_unsupported_type(self):
        with self.assertRaises(TypeError):
            convert_level_number(3.14)  # type: ignore[arg-type]

    def test_case_insensitive(self):
        self.assertEqual(convert_level_number("DEBUG"), logging.DEBUG)
        self.assertEqual(convert_level_number("Info"), logging.INFO)


class ConvertPrintableLevelTestCase(TestCase):
    def test_string_passthrough(self):
        self.assertEqual(convert_printable_level("custom"), "custom")

    def test_off(self):
        self.assertEqual(convert_printable_level(OFF), "Off")

    def test_over_critical(self):
        self.assertEqual(convert_printable_level(logging.CRITICAL + 1), "OverCritical")

    def test_critical(self):
        self.assertEqual(convert_printable_level(logging.CRITICAL), "Critical")

    def test_over_error(self):
        self.assertEqual(convert_printable_level(logging.ERROR + 1), "OverError")

    def test_error(self):
        self.assertEqual(convert_printable_level(logging.ERROR), "Error")

    def test_over_warning(self):
        self.assertEqual(convert_printable_level(logging.WARNING + 1), "OverWarning")

    def test_warning(self):
        self.assertEqual(convert_printable_level(logging.WARNING), "Warning")

    def test_over_info(self):
        self.assertEqual(convert_printable_level(logging.INFO + 1), "OverInfo")

    def test_info(self):
        self.assertEqual(convert_printable_level(logging.INFO), "Info")

    def test_over_debug(self):
        self.assertEqual(convert_printable_level(logging.DEBUG + 1), "OverDebug")

    def test_debug(self):
        self.assertEqual(convert_printable_level(logging.DEBUG), "Debug")

    def test_over_notset(self):
        self.assertEqual(convert_printable_level(logging.NOTSET + 1), "OverNotSet")

    def test_notset(self):
        self.assertEqual(convert_printable_level(logging.NOTSET), "NotSet")

    def test_negative(self):
        self.assertEqual(convert_printable_level(-1), "-1")


class SetLevelTestCase(TestCase):
    def test_set_root_level(self):
        set_root_level("warning")
        self.assertEqual(logging.getLogger().level, logging.WARNING)
        set_root_level("debug")

    def test_set_asyncio_level(self):
        set_asyncio_level("error")
        self.assertEqual(logging.getLogger("asyncio").level, logging.ERROR)
        set_asyncio_level("debug")


class SetDefaultLoggingConfigTestCase(TestCase):
    def test_set_default_logging_config(self):
        with patch("cvpa.logging.logging.dictConfig"):
            set_default_logging_config()


class LoggingConfigTestCase(TestCase):
    def test_dumps_default(self):
        result = dumps_default_logging_config("/tmp/test_cvpa")
        self.assertIn("/tmp/test_cvpa", result)
        self.assertIsInstance(result, str)

    def test_loads_logging_config(self):
        import json

        config = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {},
            "loggers": {},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(config, f)
            f.flush()
            loads_logging_config(f.name)


class AddHandlerTestCase(TestCase):
    def setUp(self):
        self._logger_name = "_cvpa_test_add_handler_"
        self._logger = logging.getLogger(self._logger_name)
        self._original_handlers = list(self._logger.handlers)

    def tearDown(self):
        self._logger.handlers = self._original_handlers

    def test_add_default_logging(self):
        add_default_logging(self._logger_name)
        self.assertGreater(len(self._logger.handlers), len(self._original_handlers))

    def test_add_simple_logging(self):
        add_simple_logging(self._logger_name)
        self.assertGreater(len(self._logger.handlers), len(self._original_handlers))

    def test_add_default_colored_logging(self):
        add_default_colored_logging(self._logger_name)
        self.assertGreater(len(self._logger.handlers), len(self._original_handlers))

    def test_add_default_rotate_file_logging(self):
        with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
            add_default_rotate_file_logging(f.name, name=self._logger_name)
            self.assertGreater(len(self._logger.handlers), len(self._original_handlers))


if __name__ == "__main__":
    main()
