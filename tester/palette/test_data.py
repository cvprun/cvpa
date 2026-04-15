# -*- coding: utf-8 -*-

from importlib import import_module
from unittest import TestCase, main

PALETTE_MODULES = (
    "cvpa.palette.basic",
    "cvpa.palette.css4",
    "cvpa.palette.extended",
    "cvpa.palette.flat",
    "cvpa.palette.tableau",
    "cvpa.palette.vga",
    "cvpa.palette.xkcd",
)


class PaletteDataTestCase(TestCase):
    def test_all_palettes_have_valid_rgb(self):
        for module_name in PALETTE_MODULES:
            module = import_module(module_name)
            for key in dir(module):
                if not key.isupper():
                    continue
                value = getattr(module, key)
                if not isinstance(value, tuple) or len(value) != 3:
                    continue
                if not all(isinstance(v, float) for v in value):
                    continue
                for v in value:
                    self.assertGreaterEqual(
                        v, 0.0, f"{module_name}.{key} has value < 0"
                    )
                    self.assertLessEqual(v, 1.0, f"{module_name}.{key} has value > 1")


if __name__ == "__main__":
    main()
