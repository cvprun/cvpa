# -*- coding: utf-8 -*-

from types import MappingProxyType
from unittest import TestCase, main

from cvpa.colors.xterm import (
    XTERM_256COLOR_MAP,
    create_256color_mapping,
    create_xterm_256color_mapping,
)


class Create256ColorMappingTestCase(TestCase):
    def test_has_256_entries(self):
        mapping = create_256color_mapping()
        self.assertEqual(len(mapping), 256)

    def test_keys_are_0_to_255(self):
        mapping = create_256color_mapping()
        self.assertEqual(set(mapping.keys()), set(range(256)))

    def test_values_are_rgb_tuples(self):
        mapping = create_256color_mapping()
        for code, rgb in mapping.items():
            self.assertEqual(len(rgb), 3, f"Code {code} has wrong tuple length")
            for c in rgb:
                self.assertIsInstance(c, int)
                self.assertGreaterEqual(c, 0)
                self.assertLessEqual(c, 255)

    def test_code_0_black(self):
        mapping = create_256color_mapping()
        self.assertEqual(mapping[0], (0, 0, 0))

    def test_code_4_special_blue(self):
        mapping = create_256color_mapping()
        r, g, b = mapping[4]
        self.assertEqual(b, 238)

    def test_code_7_level_229(self):
        mapping = create_256color_mapping()
        r, g, b = mapping[7]
        self.assertEqual(r, 229)
        self.assertEqual(g, 229)
        self.assertEqual(b, 229)

    def test_code_8_gray_127(self):
        mapping = create_256color_mapping()
        self.assertEqual(mapping[8], (127, 127, 127))

    def test_code_9_to_15_level_255(self):
        mapping = create_256color_mapping()
        for code in range(9, 16):
            r, g, b = mapping[code]
            if (code & 1) != 0:
                self.assertEqual(r, 255)
            if (code & 2) != 0:
                self.assertEqual(g, 255)
            if (code & 4) != 0:
                self.assertEqual(b, 255)

    def test_code_12_special(self):
        mapping = create_256color_mapping()
        r, g, b = mapping[12]
        self.assertEqual(r, 92)
        self.assertEqual(g, 92)

    def test_color_cube_16_to_231(self):
        mapping = create_256color_mapping()
        self.assertEqual(mapping[16], (0, 0, 0))
        self.assertEqual(mapping[231], (255, 255, 255))

    def test_grayscale_ramp_232_to_255(self):
        mapping = create_256color_mapping()
        self.assertEqual(mapping[232], (8, 8, 8))
        self.assertEqual(mapping[255], (238, 238, 238))


class CreateXterm256ColorMappingTestCase(TestCase):
    def test_returns_mapping_proxy(self):
        result = create_xterm_256color_mapping()
        self.assertIsInstance(result, MappingProxyType)

    def test_has_256_entries(self):
        self.assertEqual(len(create_xterm_256color_mapping()), 256)

    def test_module_level_constant(self):
        self.assertIsInstance(XTERM_256COLOR_MAP, MappingProxyType)
        self.assertEqual(len(XTERM_256COLOR_MAP), 256)


if __name__ == "__main__":
    main()
