# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.variables import (
    CVPA_HOME_DIRNAME,
    CVPA_TITLE,
    LOCALHOST,
    LOGGING_STEP,
    SLOW_CALLBACK_DURATION,
)


class VariablesTestCase(TestCase):
    def test_localhost(self):
        self.assertEqual(LOCALHOST, "localhost")

    def test_cvpa_title(self):
        self.assertEqual(CVPA_TITLE, "CVPA")

    def test_cvpa_home_dirname(self):
        self.assertEqual(CVPA_HOME_DIRNAME, ".cvpa")

    def test_logging_step(self):
        self.assertIsInstance(LOGGING_STEP, int)
        self.assertGreater(LOGGING_STEP, 0)

    def test_slow_callback_duration(self):
        self.assertIsInstance(SLOW_CALLBACK_DURATION, float)
        self.assertGreater(SLOW_CALLBACK_DURATION, 0)


if __name__ == "__main__":
    main()
