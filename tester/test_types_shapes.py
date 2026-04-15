# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.types.shapes import EMPTY_POINT, EMPTY_RECT, EMPTY_SIZE, ONE_POINT
from cvpa.types.shapes_i import EMPTY_POINT_I, EMPTY_SIZE_I, ONE_POINT_I


class ShapesTestCase(TestCase):
    def test_empty_point(self):
        self.assertEqual(EMPTY_POINT, (0.0, 0.0))

    def test_empty_size(self):
        self.assertEqual(EMPTY_SIZE, (0.0, 0.0))

    def test_empty_rect(self):
        self.assertEqual(EMPTY_RECT, (0.0, 0.0, 0.0, 0.0))

    def test_one_point(self):
        self.assertEqual(ONE_POINT, (1.0, 1.0))


class ShapesITestCase(TestCase):
    def test_empty_point_i(self):
        self.assertEqual(EMPTY_POINT_I, (0, 0))

    def test_empty_size_i(self):
        self.assertEqual(EMPTY_SIZE_I, (0, 0))

    def test_one_point_i(self):
        self.assertEqual(ONE_POINT_I, (1, 1))


if __name__ == "__main__":
    main()
