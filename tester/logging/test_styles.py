# -*- coding: utf-8 -*-

from logging import CRITICAL, DEBUG, ERROR, INFO, NOTSET, WARNING
from unittest import TestCase, main

from cvpa.logging.styles import GuiLoggingStyle


class GuiLoggingStyleTestCase(TestCase):
    def setUp(self):
        self.style = GuiLoggingStyle()

    def test_default_level_name(self):
        self.assertEqual(self.style.level_name, "notset")

    def test_set_level_name(self):
        self.style.level_name = "error"
        self.assertEqual(self.style.level_name, "error")

    def test_level_number(self):
        self.style.level_name = "info"
        self.assertEqual(self.style.level_number, INFO)

    def test_set_level_number(self):
        self.style.level_number = ERROR
        self.assertEqual(self.style.level_name, "error")

    def test_get_level_color_critical(self):
        color = self.style.get_level_color(CRITICAL)
        self.assertIsNotNone(color)

    def test_get_level_color_error(self):
        color = self.style.get_level_color(ERROR)
        self.assertIsNotNone(color)

    def test_get_level_color_warning(self):
        color = self.style.get_level_color(WARNING)
        self.assertIsNotNone(color)

    def test_get_level_color_info(self):
        color = self.style.get_level_color(INFO)
        self.assertIsNotNone(color)

    def test_get_level_color_debug(self):
        color = self.style.get_level_color(DEBUG)
        self.assertIsNotNone(color)

    def test_get_level_color_out_of_range(self):
        color = self.style.get_level_color(NOTSET)
        self.assertIsNone(color)

    def test_get_level_color_with_default(self):
        default = (1.0, 1.0, 1.0, 1.0)
        color = self.style.get_level_color(NOTSET, default)
        self.assertEqual(color, default)


if __name__ == "__main__":
    main()
