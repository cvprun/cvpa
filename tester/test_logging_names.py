# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.logging.names import CVPA_AGENT_LOGGER_NAME, CVPA_LOGGER_NAME


class LoggingNamesTestCase(TestCase):
    def test_logger_name(self):
        self.assertEqual(CVPA_LOGGER_NAME, "cvpa")

    def test_agent_logger_name(self):
        self.assertTrue(CVPA_AGENT_LOGGER_NAME.startswith(CVPA_LOGGER_NAME))


if __name__ == "__main__":
    main()
