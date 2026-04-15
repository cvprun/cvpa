# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.types.colors import (
    BLACK_RGB,
    BLACK_RGBA,
    WHITE_RGB,
    WHITE_RGBA,
)


class TypesColorsTestCase(TestCase):
    def test_black_rgb(self):
        self.assertEqual(BLACK_RGB, (0.0, 0.0, 0.0))

    def test_black_rgba(self):
        self.assertEqual(BLACK_RGBA, (0.0, 0.0, 0.0, 1.0))

    def test_white_rgb(self):
        self.assertEqual(WHITE_RGB, (1.0, 1.0, 1.0))

    def test_white_rgba(self):
        self.assertEqual(WHITE_RGBA, (1.0, 1.0, 1.0, 1.0))


if __name__ == "__main__":
    main()
