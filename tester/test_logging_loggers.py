# -*- coding: utf-8 -*-

import logging
from unittest import TestCase, main

from cvpa.logging.loggers import agent_logger, logger


class LoggersTestCase(TestCase):
    def test_logger_instance(self):
        self.assertIsInstance(logger, logging.Logger)

    def test_agent_logger_instance(self):
        self.assertIsInstance(agent_logger, logging.Logger)


if __name__ == "__main__":
    main()
