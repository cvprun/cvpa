# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from logging import DEBUG, Logger, getLogger
from unittest import TestCase, main
from unittest.mock import MagicMock

from cvpa.logging.profile import ProfileLogging


class ProfileLoggingInitTestCase(TestCase):
    def test_with_string_logger(self):
        p = ProfileLogging(logger="test_profile")
        self.assertIsInstance(p._logger, Logger)

    def test_with_logger_instance(self):
        logger = getLogger("test_profile2")
        p = ProfileLogging(logger=logger)
        self.assertIs(p._logger, logger)

    def test_with_custom_strfmt(self):
        p = ProfileLogging(strfmt="custom {iter}")
        self.assertEqual(p._strfmt, "custom {iter}")

    def test_with_prefix(self):
        p = ProfileLogging(prefix="my_prefix")
        self.assertEqual(p.prefix, "my_prefix")
        self.assertIn("{prefix}", p._strfmt)

    def test_without_prefix(self):
        p = ProfileLogging()
        self.assertIsNone(p.prefix)
        self.assertNotIn("{prefix}", p._strfmt)


class ProfileLoggingPropertiesTestCase(TestCase):
    def test_step_properties(self):
        p = ProfileLogging(threshold=1)
        t1 = datetime(2024, 1, 1, 0, 0, 0)
        t2 = datetime(2024, 1, 1, 0, 0, 1)
        p.begin(dt=t1)
        p._end = t2
        self.assertEqual(p.step_iteration, 1)
        self.assertEqual(p.total_iteration, 1)

    def test_duration(self):
        p = ProfileLogging()
        p._begin = datetime(2024, 1, 1, 0, 0, 0)
        p._end = datetime(2024, 1, 1, 0, 0, 5)
        self.assertEqual(p.duration, timedelta(seconds=5))
        self.assertEqual(p.duration_seconds, 5.0)


class ProfileLoggingCycleTestCase(TestCase):
    def test_begin_end_cycle(self):
        mock_logger = MagicMock(spec=Logger)
        p = ProfileLogging(logger=mock_logger, threshold=2)

        t1 = datetime(2024, 1, 1, 0, 0, 0)
        t2 = datetime(2024, 1, 1, 0, 0, 1)
        p.begin(dt=t1)
        p.end(dt=t2)
        self.assertEqual(p.total_iteration, 1)
        self.assertFalse(mock_logger.log.called)

        t3 = datetime(2024, 1, 1, 0, 0, 2)
        t4 = datetime(2024, 1, 1, 0, 0, 3)
        p.begin(dt=t3)
        p.end(dt=t4)
        self.assertTrue(mock_logger.log.called)
        self.assertEqual(p._step_iteration, 0)

    def test_is_emit(self):
        p = ProfileLogging(threshold=3)
        self.assertTrue(p.is_emit())
        p._step_iteration = 1
        self.assertFalse(p.is_emit())
        p._step_iteration = 3
        self.assertTrue(p.is_emit())

    def test_reset(self):
        p = ProfileLogging()
        p._step_iteration = 5
        p._step_duration = 10.0
        p.reset()
        self.assertEqual(p._step_iteration, 0)
        self.assertEqual(p._step_duration, 0.0)

    def test_fmt(self):
        p = ProfileLogging(threshold=1)
        p.begin(dt=datetime(2024, 1, 1))
        p._end = datetime(2024, 1, 1, 0, 0, 1)
        p._step_duration = 1.0
        result = p.fmt()
        self.assertIn("Step #1", result)

    def test_step_average(self):
        p = ProfileLogging()
        p._step_iteration = 2
        p._step_duration = 4.0
        self.assertEqual(p.step_average, 2.0)

    def test_total_average(self):
        p = ProfileLogging()
        p._total_iteration = 4
        p._total_duration = 8.0
        self.assertEqual(p.total_average, 2.0)

    def test_total_duration(self):
        p = ProfileLogging()
        p._total_duration = 5.0
        self.assertEqual(p.total_duration, 5.0)

    def test_step_duration(self):
        p = ProfileLogging()
        p._step_duration = 3.0
        self.assertEqual(p.step_duration, 3.0)


class ProfileLoggingContextManagerTestCase(TestCase):
    def test_context_manager(self):
        p = ProfileLogging(threshold=1)
        mock_logger = MagicMock()
        p._logger = mock_logger

        with p:
            pass

        self.assertEqual(p.total_iteration, 1)


if __name__ == "__main__":
    main()
