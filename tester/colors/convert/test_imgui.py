# -*- coding: utf-8 -*-

from unittest import TestCase, main

from cvpa.colors.convert.imgui import (
    argb8888_to_uint32,
    rgb_to_uint32,
    rgba_to_uint32,
    uint32_to_rgb,
    uint32_to_rgba,
)


class Argb8888ToUint32TestCase(TestCase):
    def test_black(self):
        self.assertEqual(argb8888_to_uint32(255, 0, 0, 0), 0xFF000000)

    def test_white(self):
        self.assertEqual(argb8888_to_uint32(255, 255, 255, 255), 0xFFFFFFFF)

    def test_red(self):
        self.assertEqual(argb8888_to_uint32(255, 255, 0, 0), 0xFFFF0000)

    def test_zero_alpha(self):
        self.assertEqual(argb8888_to_uint32(0, 0, 0, 0), 0x00000000)

    def test_boundary_values(self):
        self.assertEqual(argb8888_to_uint32(0, 0, 0, 255), 0x000000FF)
        self.assertEqual(argb8888_to_uint32(0, 0, 255, 0), 0x0000FF00)

    def test_negative_value_raises(self):
        with self.assertRaises(ValueError):
            argb8888_to_uint32(-1, 0, 0, 0)

    def test_over_255_raises(self):
        with self.assertRaises(ValueError):
            argb8888_to_uint32(256, 0, 0, 0)


class RgbaToUint32TestCase(TestCase):
    def test_black(self):
        self.assertEqual(rgba_to_uint32((0.0, 0.0, 0.0, 1.0)), 0xFF000000)

    def test_white(self):
        self.assertEqual(rgba_to_uint32((1.0, 1.0, 1.0, 1.0)), 0xFFFFFFFF)

    def test_zero_alpha(self):
        self.assertEqual(rgba_to_uint32((0.0, 0.0, 0.0, 0.0)), 0x00000000)

    def test_invalid_r_raises(self):
        with self.assertRaises(ValueError):
            rgba_to_uint32((1.1, 0.0, 0.0, 1.0))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            rgba_to_uint32((-0.1, 0.0, 0.0, 1.0))


class RgbToUint32TestCase(TestCase):
    def test_black_default_alpha(self):
        self.assertEqual(rgb_to_uint32((0.0, 0.0, 0.0)), 0xFF000000)

    def test_white_default_alpha(self):
        self.assertEqual(rgb_to_uint32((1.0, 1.0, 1.0)), 0xFFFFFFFF)

    def test_custom_alpha(self):
        self.assertEqual(rgb_to_uint32((0.0, 0.0, 0.0), a=0.0), 0x00000000)

    def test_invalid_rgb_raises(self):
        with self.assertRaises(ValueError):
            rgb_to_uint32((1.1, 0.0, 0.0))

    def test_invalid_alpha_raises(self):
        with self.assertRaises(ValueError):
            rgb_to_uint32((0.0, 0.0, 0.0), a=1.1)


class Uint32ToRgbaTestCase(TestCase):
    def test_black(self):
        self.assertEqual(uint32_to_rgba(0xFF000000), (0.0, 0.0, 0.0, 1.0))

    def test_white(self):
        self.assertEqual(uint32_to_rgba(0xFFFFFFFF), (1.0, 1.0, 1.0, 1.0))

    def test_zero(self):
        self.assertEqual(uint32_to_rgba(0x00000000), (0.0, 0.0, 0.0, 0.0))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            uint32_to_rgba(-1)

    def test_over_max_raises(self):
        with self.assertRaises(ValueError):
            uint32_to_rgba(0x1FFFFFFFF)


class Uint32ToRgbTestCase(TestCase):
    def test_black(self):
        self.assertEqual(uint32_to_rgb(0xFF000000), (0.0, 0.0, 0.0))

    def test_white(self):
        self.assertEqual(uint32_to_rgb(0xFFFFFFFF), (1.0, 1.0, 1.0))

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            uint32_to_rgb(-1)

    def test_over_max_raises(self):
        with self.assertRaises(ValueError):
            uint32_to_rgb(0x1FFFFFFFF)


class RoundTripTestCase(TestCase):
    def test_rgba_round_trip(self):
        original = (0.5, 0.25, 0.75, 1.0)
        result = uint32_to_rgba(rgba_to_uint32(original))
        for o, r in zip(original, result):
            self.assertAlmostEqual(o, r, places=2)

    def test_rgb_round_trip(self):
        original = (0.5, 0.25, 0.75)
        result = uint32_to_rgb(rgb_to_uint32(original))
        for o, r in zip(original, result):
            self.assertAlmostEqual(o, r, places=2)


if __name__ == "__main__":
    main()
