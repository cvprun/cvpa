# -*- coding: utf-8 -*-

import logging
from unittest import TestCase, main

from cvpa.logging.records.formatted import FormattedLogRecord


class FormattedLogRecordTestCase(TestCase):
    def setUp(self):
        self.record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="hello %s",
            args=("world",),
            exc_info=None,
            func="test_func",
        )
        self.formatted = FormattedLogRecord(self.record, "hello world")

    def test_from_log(self):
        result = FormattedLogRecord.from_log(self.record, "hello world")
        self.assertIsInstance(result, FormattedLogRecord)
        self.assertEqual(result.formatted_message, "hello world")

    def test_args(self):
        self.assertEqual(self.formatted.args, ("world",))

    def test_created(self):
        self.assertEqual(self.formatted.created, self.record.created)

    def test_exc_info(self):
        self.assertIsNone(self.formatted.exc_info)

    def test_exc_text(self):
        self.assertIsNone(self.formatted.exc_text)

    def test_filename(self):
        self.assertEqual(self.formatted.filename, "test.py")

    def test_func_name(self):
        self.assertEqual(self.formatted.func_name, "test_func")

    def test_levelname(self):
        self.assertEqual(self.formatted.levelname, "INFO")

    def test_levelno(self):
        self.assertEqual(self.formatted.levelno, logging.INFO)

    def test_lineno(self):
        self.assertEqual(self.formatted.lineno, 42)

    def test_module(self):
        self.assertEqual(self.formatted.module, "test")

    def test_msecs(self):
        self.assertIsInstance(self.formatted.msecs, float)

    def test_msg(self):
        self.assertEqual(self.formatted.msg, "hello %s")

    def test_name(self):
        self.assertEqual(self.formatted.name, "test")

    def test_pathname(self):
        self.assertEqual(self.formatted.pathname, "test.py")

    def test_process(self):
        self.assertIsNotNone(self.formatted.process)

    def test_process_name(self):
        self.assertIsNotNone(self.formatted.process_name)

    def test_relative_created(self):
        self.assertIsInstance(self.formatted.relative_created, float)

    def test_stack_info(self):
        self.assertIsNone(self.formatted.stack_info)

    def test_thread(self):
        self.assertIsNotNone(self.formatted.thread)

    def test_thread_name(self):
        self.assertIsNotNone(self.formatted.thread_name)

    def test_asctime(self):
        formatter = logging.Formatter("%(asctime)s %(message)s")
        formatter.format(self.record)
        self.assertIsNotNone(self.formatted.asctime)


if __name__ == "__main__":
    main()
