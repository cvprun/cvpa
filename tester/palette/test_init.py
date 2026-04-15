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
        self.assertEqual(16, len(basic_palette()))

    def test_css4(self):
        self.assertEqual(148, len(css4_palette()))

    def test_extended(self):
        self.assertEqual(140, len(extended_palette()))

    def test_flat(self):
        self.assertEqual(240, len(flat_palette()))

    def test_tableau(self):
        self.assertEqual(10, len(tableau_palette()))

    def test_vga(self):
        self.assertEqual(16, len(vga_palette()))

    def test_xkcd(self):
        self.assertEqual(938, len(xkcd_palette()))


class GlobalPaletteTestCase(TestCase):
    def test_global_map(self):
        m = global_palette_map()
        self.assertEqual(len(m), 7)

    def test_registered_keys(self):
        expect_names = {"basic", "css4", "extended", "flat", "tableau", "vga", "xkcd"}
        actual_names = set(registered_palette_keys())
        self.assertSetEqual(expect_names, actual_names)

    def test_registered_count(self):
        expect_count = sum(
            (
                len(basic_palette()),
                len(css4_palette()),
                len(extended_palette()),
                len(flat_palette()),
                len(tableau_palette()),
                len(vga_palette()),
                len(xkcd_palette()),
            )
        )
        self.assertEqual(expect_count, registered_color_count())


class FindNamedColorTestCase(TestCase):
    def test_with_palette_prefix(self):
        from cvpa.palette import basic

        result = find_named_color("basic:WHITE")
        self.assertTupleEqual(basic.WHITE, result)

    def test_without_prefix(self):
        from cvpa.palette import extended

        result = find_named_color(" dimgray ")
        self.assertTupleEqual(extended.DIMGRAY, result)

    def test_with_spaces(self):
        from cvpa.palette import extended

        result = find_named_color("extended : beige")
        self.assertTupleEqual(extended.BEIGE, result)

    def test_xkcd_with_space(self):
        from cvpa.palette import xkcd

        result = find_named_color("xkcd: nasty green")
        self.assertTupleEqual(xkcd.NASTY_GREEN, result)

    def test_case_insensitive(self):
        result = find_named_color("basic:white")
        self.assertIsNotNone(result)

    def test_unknown_palette(self):
        result = find_named_color("nonexistent:RED")
        self.assertIsNone(result)

    def test_unknown_color(self):
        result = find_named_color("basic:NONEXISTENT_COLOR_XYZ")
        self.assertIsNone(result)


if __name__ == "__main__":
    main()
