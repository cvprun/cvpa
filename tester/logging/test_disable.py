# -*- coding: utf-8 -*-

import logging
from unittest import TestCase, main

from cvpa.logging.disable import disable_logging


class DisableLoggingTestCase(TestCase):
    def test_disables_and_restores(self):
        original = logging.root.manager.disable
        with disable_logging():
            self.assertEqual(logging.root.manager.disable, logging.CRITICAL)
        self.assertEqual(logging.root.manager.disable, original)

    def test_custom_level(self):
        with disable_logging(logging.WARNING):
            self.assertEqual(logging.root.manager.disable, logging.WARNING)


if __name__ == "__main__":
    main()
