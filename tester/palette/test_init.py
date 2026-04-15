# -*- coding: utf-8 -*-

from types import ModuleType
from unittest import TestCase, main

from cvpa.palette import (
    _load_palette_from_module,
    _palette_filter,
    basic_palette,
    css4_palette,
    extended_palette,
    find_named_color,
    flat_palette,
    global_palette_map,
    registered_color_count,
    registered_palette_keys,
    tableau_palette,
    vga_palette,
    xkcd_palette,
)


class PaletteFilterTestCase(TestCase):
    def test_non_upper_key(self):
        m = ModuleType("test")
        m.lower = (0.0, 0.0, 0.0)  # type: ignore[attr-defined]
        self.assertFalse(_palette_filter(m, "lower"))

    def test_non_tuple(self):
        m = ModuleType("test")
        m.VALUE = "not a tuple"  # type: ignore[attr-defined]
        self.assertFalse(_palette_filter(m, "VALUE"))

    def test_wrong_length(self):
        m = ModuleType("test")
        m.VALUE = (0.0, 0.0)  # type: ignore[attr-defined]
        self.assertFalse(_palette_filter(m, "VALUE"))

    def test_non_float_first(self):
        m = ModuleType("test")
        m.VALUE = (1, 0.0, 0.0)  # type: ignore[attr-defined]
        self.assertFalse(_palette_filter(m, "VALUE"))

    def test_non_float_second(self):
        m = ModuleType("test")
        m.VALUE = (0.0, 1, 0.0)  # type: ignore[attr-defined]
        self.assertFalse(_palette_filter(m, "VALUE"))

    def test_non_float_third(self):
        m = ModuleType("test")
        m.VALUE = (0.0, 0.0, 1)  # type: ignore[attr-defined]
        self.assertFalse(_palette_filter(m, "VALUE"))

    def test_valid(self):
        m = ModuleType("test")
        m.RED = (1.0, 0.0, 0.0)  # type: ignore[attr-defined]
        self.assertTrue(_palette_filter(m, "RED"))


class LoadPaletteTestCase(TestCase):
    def test_load_module(self):
        m = ModuleType("test")
        m.RED = (1.0, 0.0, 0.0)  # type: ignore[attr-defined]
        m.lower = (0.0, 0.0, 0.0)  # type: ignore[attr-defined]
        result = _load_palette_from_module(m)
        self.assertIn("RED", result)
        self.assertNotIn("lower", result)


class PaletteLoadersTestCase(TestCase):
    def test_basic(self):
        self.assertGreater(len(basic_palette()), 0)

    def test_css4(self):
        self.assertGreater(len(css4_palette()), 0)

    def test_extended(self):
        self.assertGreater(len(extended_palette()), 0)

    def test_flat(self):
        self.assertGreater(len(flat_palette()), 0)

    def test_tableau(self):
        self.assertGreater(len(tableau_palette()), 0)

    def test_vga(self):
        self.assertGreater(len(vga_palette()), 0)

    def test_xkcd(self):
        self.assertGreater(len(xkcd_palette()), 0)


class GlobalPaletteTestCase(TestCase):
    def test_global_map(self):
        m = global_palette_map()
        self.assertEqual(len(m), 7)

    def test_registered_keys(self):
        keys = registered_palette_keys()
        self.assertEqual(len(keys), 7)

    def test_registered_count(self):
        count = registered_color_count()
        self.assertGreater(count, 0)


class FindNamedColorTestCase(TestCase):
    def test_with_palette_prefix(self):
        result = find_named_color("basic:BLACK")
        self.assertIsNotNone(result)

    def test_without_prefix(self):
        result = find_named_color("RED")
        self.assertIsNotNone(result)

    def test_unknown_palette(self):
        result = find_named_color("nonexistent:RED")
        self.assertIsNone(result)

    def test_unknown_color(self):
        result = find_named_color("basic:NONEXISTENT_COLOR_XYZ")
        self.assertIsNone(result)


if __name__ == "__main__":
    main()
